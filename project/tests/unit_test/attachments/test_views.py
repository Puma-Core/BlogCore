import json
from urllib.parse import urlsplit

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import resolve, reverse
from storages.backends.s3 import S3Storage

from attachments.models import Attachment
from attachments.views import AttachmentDetailView, AttachmentUploadView


pytestmark = pytest.mark.usefixtures("local_attachment_storage")


def image_file(name="image.jpg", content_type="image/jpeg", content=b"image"):
    return SimpleUploadedFile(name, content, content_type=content_type)


def public_remote_storage_settings():
    return {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "access_key": "access-key",
                "secret_key": "secret-key",
                "bucket_name": "blog-media",
                "endpoint_url": "https://objects.example.test",
                "region_name": "us-east-1",
                "custom_domain": "media.example.test",
                "querystring_auth": False,
            },
        },
        "staticfiles": settings.STORAGES["staticfiles"],
    }


@pytest.mark.django_db
def test_upload_requires_authentication(api_client) -> None:
    response = api_client.post(reverse("attachment-upload"), {"file": image_file()})

    assert response.status_code == 403
    assert Attachment.objects.count() == 0


@pytest.mark.django_db
def test_upload_requires_a_file(api_client, persisted_user) -> None:
    api_client.force_authenticate(persisted_user)

    response = api_client.post(reverse("attachment-upload"), {})

    assert response.status_code == 400
    assert response.data == {"file": "An image file is required."}


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("name", "content_type"),
    (("image.jpg", "image/jpeg"), ("image.jpeg", "image/jpeg"), ("image.webp", "image/webp")),
)
def test_upload_stores_supported_images_and_returns_vditor_response(
    api_client, persisted_user, tmp_path, name, content_type
) -> None:
    api_client.force_authenticate(persisted_user)
    with override_settings(MEDIA_ROOT=tmp_path):
        response = api_client.post(
            reverse("attachment-upload"),
            {"file": image_file(name, content_type), "metadata": json.dumps({"relationship": {"posts": [1]}})},
        )

    attachment = Attachment.objects.get()
    url = f"http://testserver{attachment.file.url}"
    assert response.status_code == 201
    assert response.data == {
        "code": 0,
        "msg": "",
        "data": {
            "id": str(attachment.id),
            "url": url,
            "errFiles": [],
            "succMap": {name: url},
        },
    }
    assert attachment.owner == persisted_user
    assert attachment.metadata == {"relationship": {"posts": [1]}}
    assert (tmp_path / attachment.file.name).is_file()


@pytest.mark.django_db
def test_upload_returns_an_unsigned_custom_domain_url(api_client, persisted_user, mocker) -> None:
    api_client.force_authenticate(persisted_user)
    mocker.patch.object(S3Storage, "exists", return_value=False)
    mocker.patch.object(S3Storage, "_save", side_effect=lambda name, content: name)

    with override_settings(STORAGES=public_remote_storage_settings()):
        response = api_client.post(reverse("attachment-upload"), {"file": image_file()})

    url = response.data["data"]["url"]
    assert response.status_code == 201
    assert url.startswith("https://media.example.test/attachments/")
    assert urlsplit(url).query == ""


@pytest.mark.django_db
def test_upload_accepts_a_raw_jpeg_request(api_client, persisted_user, tmp_path) -> None:
    api_client.force_authenticate(persisted_user)
    with override_settings(MEDIA_ROOT=tmp_path):
        response = api_client.post(
            reverse("attachment-upload"),
            b"image",
            content_type="image/jpeg",
            HTTP_CONTENT_DISPOSITION='attachment; filename="image.jpeg"',
        )

    attachment = Attachment.objects.get()
    assert response.status_code == 201
    assert attachment.original_name == "image.jpeg"
    assert attachment.mime_type == "image/jpeg"


@pytest.mark.django_db
@pytest.mark.parametrize("content_type", ("image/png", "image/gif", "text/plain"))
def test_upload_rejects_unsupported_media_types(api_client, persisted_user, content_type) -> None:
    api_client.force_authenticate(persisted_user)

    response = api_client.post(reverse("attachment-upload"), {"file": image_file(content_type=content_type)})

    assert response.status_code == 400
    assert Attachment.objects.count() == 0


@pytest.mark.django_db
def test_upload_rejects_oversized_files(api_client, persisted_user) -> None:
    api_client.force_authenticate(persisted_user)
    with override_settings(POST_ATTACHMENT_MAX_SIZE=3):
        response = api_client.post(reverse("attachment-upload"), {"file": image_file(content=b"long")})

    assert response.status_code == 400
    assert Attachment.objects.count() == 0


@pytest.mark.django_db
def test_upload_rejects_invalid_metadata_without_writing_a_file(
    api_client, persisted_user, tmp_path
) -> None:
    api_client.force_authenticate(persisted_user)
    with override_settings(MEDIA_ROOT=tmp_path):
        response = api_client.post(
            reverse("attachment-upload"),
            {"file": image_file(), "metadata": "not-json"},
        )

    assert response.status_code == 400
    assert Attachment.objects.count() == 0
    assert list(tmp_path.iterdir()) == []


@pytest.mark.django_db
def test_upload_rejects_metadata_that_is_not_an_object(api_client, persisted_user) -> None:
    api_client.force_authenticate(persisted_user)

    response = api_client.post(
        reverse("attachment-upload"),
        {"file": image_file(), "metadata": json.dumps(["not", "an", "object"])},
    )

    assert response.status_code == 400
    assert response.data == {"metadata": "Metadata must be a JSON object."}


@pytest.mark.django_db
def test_upload_deletes_the_file_when_persistence_fails(
    api_client, persisted_user, mocker, tmp_path
) -> None:
    api_client.force_authenticate(persisted_user)
    mock_save = mocker.patch.object(Attachment, "save", side_effect=RuntimeError)
    mock_log = mocker.patch("attachments.views.logger.exception")

    with override_settings(MEDIA_ROOT=tmp_path), pytest.raises(RuntimeError):
        api_client.post(reverse("attachment-upload"), {"file": image_file()})

    mock_save.assert_called_once()
    mock_log.assert_called_once_with(
        "Attachment record creation failed",
        extra=mocker.ANY,
    )
    assert not [path for path in tmp_path.rglob("*") if path.is_file()]


@pytest.mark.django_db
def test_upload_preserves_the_record_error_when_cleanup_fails(
    api_client, persisted_user, mocker
) -> None:
    api_client.force_authenticate(persisted_user)
    mocker.patch.object(Attachment, "save", side_effect=RuntimeError("record failed"))
    mocker.patch(
        "django.db.models.fields.files.FieldFile.delete",
        side_effect=RuntimeError("cleanup failed"),
    )
    mock_log = mocker.patch("attachments.views.logger.exception")

    with pytest.raises(RuntimeError, match="record failed"):
        api_client.post(reverse("attachment-upload"), {"file": image_file()})

    assert mock_log.call_args_list == [
        mocker.call("Attachment record creation failed", extra=mocker.ANY),
        mocker.call("Attachment storage cleanup failed", extra=mocker.ANY),
    ]


@pytest.mark.django_db
def test_upload_does_not_try_to_delete_when_storage_upload_fails(
    api_client, persisted_user, mocker
) -> None:
    api_client.force_authenticate(persisted_user)
    mock_save = mocker.patch.object(Attachment, "save")
    mock_upload = mocker.patch(
        "django.db.models.fields.files.FieldFile.save",
        side_effect=RuntimeError("storage failed"),
    )
    mock_delete = mocker.patch("django.db.models.fields.files.FieldFile.delete")
    mock_log = mocker.patch("attachments.views.logger.exception")

    with pytest.raises(RuntimeError, match="storage failed"):
        api_client.post(reverse("attachment-upload"), {"file": image_file()})

    mock_upload.assert_called_once()
    mock_save.assert_not_called()
    mock_delete.assert_not_called()
    mock_log.assert_called_once_with(
        "Attachment file upload failed",
        extra={
            "storage_backend": "django.core.files.storage.FileSystemStorage",
            "attachment_name": "image.jpg",
        },
    )


@pytest.mark.django_db
def test_uploads_with_matching_names_have_distinct_urls(api_client, persisted_user, tmp_path) -> None:
    api_client.force_authenticate(persisted_user)
    with override_settings(MEDIA_ROOT=tmp_path):
        first = api_client.post(reverse("attachment-upload"), {"file": image_file()})
        second = api_client.post(reverse("attachment-upload"), {"file": image_file()})

    assert first.data["data"]["url"] != second.data["data"]["url"]
    assert Attachment.objects.count() == 2


@pytest.mark.django_db
def test_only_the_owner_can_manage_or_delete_an_attachment(
    api_client, persisted_user, user_factory, tmp_path
) -> None:
    with override_settings(MEDIA_ROOT=tmp_path):
        attachment = Attachment.objects.create(
            file=image_file(),
            original_name="image.jpg",
            mime_type="image/jpeg",
            size=5,
            owner=persisted_user,
            metadata={"relationship": {"posts": [99]}},
        )
    other_user = user_factory(username="other-user")
    other_user.save()
    api_client.force_authenticate(other_user)
    url = reverse("attachment-detail", kwargs={"pk": attachment.pk})

    assert api_client.get(url).status_code == 404
    assert api_client.delete(url).status_code == 404
    assert Attachment.objects.filter(pk=attachment.pk, owner=persisted_user).exists()


@pytest.mark.django_db
def test_owner_can_retrieve_an_attachment(api_client, persisted_user, tmp_path) -> None:
    with override_settings(MEDIA_ROOT=tmp_path):
        attachment = Attachment.objects.create(
            file=image_file(),
            original_name="image.jpg",
            mime_type="image/jpeg",
            size=5,
            owner=persisted_user,
            metadata={"relationship": {"posts": [1]}},
        )
        api_client.force_authenticate(persisted_user)
        response = api_client.get(
            reverse("attachment-detail", kwargs={"pk": attachment.pk})
        )

    assert response.status_code == 200
    assert response.data == {
        "id": str(attachment.id),
        "url": f"http://testserver{attachment.file.url}",
        "original_name": "image.jpg",
        "mime_type": "image/jpeg",
        "size": 5,
        "metadata": {"relationship": {"posts": [1]}},
    }


@pytest.mark.django_db
def test_attachment_detail_returns_an_unsigned_custom_domain_url(api_client, persisted_user) -> None:
    attachment = Attachment.objects.create(
        file="attachments/image.jpg",
        original_name="image.jpg",
        mime_type="image/jpeg",
        size=5,
        owner=persisted_user,
    )
    api_client.force_authenticate(persisted_user)

    with override_settings(STORAGES=public_remote_storage_settings()):
        response = api_client.get(reverse("attachment-detail", kwargs={"pk": attachment.pk}))

    assert response.status_code == 200
    assert response.data["url"] == "https://media.example.test/attachments/image.jpg"
    assert urlsplit(response.data["url"]).query == ""


@pytest.mark.django_db
def test_owner_can_delete_an_attachment(api_client, persisted_user, tmp_path) -> None:
    with override_settings(MEDIA_ROOT=tmp_path):
        attachment = Attachment.objects.create(
            file=image_file(),
            original_name="image.jpg",
            mime_type="image/jpeg",
            size=5,
            owner=persisted_user,
        )
        stored_file = tmp_path / attachment.file.name
        api_client.force_authenticate(persisted_user)
        response = api_client.delete(
            reverse("attachment-detail", kwargs={"pk": attachment.pk})
        )

    assert response.status_code == 204
    assert not Attachment.objects.filter(pk=attachment.pk).exists()
    assert not stored_file.exists()


def test_attachment_routes_resolve() -> None:
    assert resolve("/api/attachments/upload/").func.cls is AttachmentUploadView
    assert resolve("/api/attachments/00000000-0000-0000-0000-000000000000/").func.cls is AttachmentDetailView
