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
