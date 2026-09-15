import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import resolve, reverse

from attachments.models import Attachment
from attachments.views import AttachmentDetailView, AttachmentUploadView


def image_file(name="image.jpg", content_type="image/jpeg", content=b"image"):
    return SimpleUploadedFile(name, content, content_type=content_type)


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
    api_client, persisted_user, mocker
) -> None:
    api_client.force_authenticate(persisted_user)
    mock_save = mocker.patch.object(Attachment, "save", side_effect=RuntimeError)
    mock_delete = mocker.patch("django.core.files.storage.FileSystemStorage.delete")

    with pytest.raises(RuntimeError):
        api_client.post(reverse("attachment-upload"), {"file": image_file()})

    mock_save.assert_called_once()
    mock_delete.assert_called_once_with("image.jpg")


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
