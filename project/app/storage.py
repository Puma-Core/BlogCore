from django.core.exceptions import ImproperlyConfigured


S3_MEDIA_STORAGE_BACKEND = "storages.backends.s3boto3.S3Boto3Storage"


def validate_s3_media_storage(backend: str, bucket_name: str | None) -> None:
    if backend == S3_MEDIA_STORAGE_BACKEND and not bucket_name:
        raise ImproperlyConfigured(
            "AWS_STORAGE_BUCKET_NAME is required when using the S3 media storage backend."
        )
