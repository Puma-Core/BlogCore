import importlib

import app.settings as app_settings


def test_s3_media_storage_settings_include_environment_options(monkeypatch):
    values = {
        "MEDIA_STORAGE_BACKEND": "storages.backends.s3.S3Storage",
        "AWS_STORAGE_BUCKET_NAME": "blog-media",
        "AWS_ACCESS_KEY_ID": "access-key",
        "AWS_SECRET_ACCESS_KEY": "secret-key",
        "AWS_S3_ENDPOINT_URL": "https://objects.example.test",
        "AWS_S3_REGION_NAME": "us-east-1",
        "AWS_S3_ADDRESSING_STYLE": "path",
        "AWS_S3_CUSTOM_DOMAIN": "media.example.test",
        "AWS_QUERYSTRING_AUTH": "false",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    importlib.reload(app_settings)

    assert app_settings.STORAGES["default"]["OPTIONS"] == {
        "access_key": "access-key",
        "secret_key": "secret-key",
        "bucket_name": "blog-media",
        "endpoint_url": "https://objects.example.test",
        "region_name": "us-east-1",
        "addressing_style": "path",
        "custom_domain": "media.example.test",
        "querystring_auth": False,
    }

    monkeypatch.undo()
    importlib.reload(app_settings)
