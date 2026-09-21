from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import DefaultStorage, storages
from django.test import override_settings
from storages.backends.s3 import S3Storage

from attachments.models import Attachment


def test_default_attachment_storage_uses_the_configured_media_backend() -> None:
    assert settings.STORAGES["default"]["BACKEND"] == settings.MEDIA_STORAGE_BACKEND


def test_default_attachment_media_settings_are_local_and_restricted() -> None:
    assert settings.MEDIA_URL == "/media/"
    assert settings.MEDIA_ROOT == Path(settings.BASE_DIR) / "media"
    assert settings.POST_ATTACHMENT_MAX_SIZE == 5 * 1024 * 1024
    assert settings.POST_ATTACHMENT_ALLOWED_MIME_TYPES == ("image/jpeg", "image/webp")


def test_attachment_file_uses_the_default_storage() -> None:
    assert isinstance(Attachment._meta.get_field("file").storage, DefaultStorage)


def test_s3_storage_is_selected_without_connecting_to_a_remote_service(mocker) -> None:
    storage_settings = {
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
    mock_save = mocker.patch.object(S3Storage, "_save", return_value="attachments/image.jpg")
    mock_delete = mocker.patch.object(S3Storage, "delete")

    with override_settings(STORAGES=storage_settings):
        storage = storages["default"]
        attachment = Attachment()
        attachment.file.save("image.jpg", ContentFile(b"image"), save=False)
        attachment.file.delete(save=False)

    assert isinstance(storage, S3Storage)
    assert storage.bucket_name == "blog-media"
    assert storage.endpoint_url == "https://objects.example.test"
    assert storage.custom_domain == "media.example.test"
    assert storage.querystring_auth is False
    assert storage.url("attachments/image.jpg") == "https://media.example.test/attachments/image.jpg"
    mock_save.assert_called_once()
    mock_delete.assert_called_once_with("attachments/image.jpg")
