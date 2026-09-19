import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def persisted_user(user_factory):
    user = user_factory()
    user.save()
    return user


@pytest.fixture
def local_attachment_storage(settings) -> None:
    settings.STORAGES = {
        **settings.STORAGES,
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    }
