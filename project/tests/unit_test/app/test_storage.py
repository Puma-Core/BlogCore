import pytest
from django.core.exceptions import ImproperlyConfigured

from app.storage import S3_MEDIA_STORAGE_BACKEND, validate_s3_media_storage


def test_local_storage_does_not_require_an_s3_bucket() -> None:
    validate_s3_media_storage("django.core.files.storage.FileSystemStorage", None)


def test_s3_storage_accepts_a_bucket_without_explicit_credentials() -> None:
    validate_s3_media_storage(S3_MEDIA_STORAGE_BACKEND, "blog-media")


def test_s3_storage_requires_a_bucket() -> None:
    with pytest.raises(ImproperlyConfigured, match="AWS_STORAGE_BUCKET_NAME"):
        validate_s3_media_storage(S3_MEDIA_STORAGE_BACKEND, None)
