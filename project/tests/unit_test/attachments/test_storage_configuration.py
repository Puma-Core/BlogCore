from pathlib import Path

from django.conf import settings


def test_default_attachment_storage_uses_the_configured_media_backend() -> None:
    assert settings.STORAGES["default"]["BACKEND"] == settings.MEDIA_STORAGE_BACKEND


def test_default_attachment_media_settings_are_local_and_restricted() -> None:
    assert settings.MEDIA_URL == "/media/"
    assert settings.MEDIA_ROOT == Path(settings.BASE_DIR) / "media"
    assert settings.POST_ATTACHMENT_MAX_SIZE == 5 * 1024 * 1024
    assert settings.POST_ATTACHMENT_ALLOWED_MIME_TYPES == ("image/jpeg", "image/webp")
