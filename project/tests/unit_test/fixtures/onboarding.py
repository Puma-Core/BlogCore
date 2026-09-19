import pytest
from django.contrib import admin

from profiles.admin.public_profile import PublicProfileAdmin
from profiles.middleware import PublicProfileOnboardingMiddleware
from profiles.models import PublicProfile


@pytest.fixture
def public_profile_admin() -> PublicProfileAdmin:
    return PublicProfileAdmin(PublicProfile, admin.site)


@pytest.fixture
def onboarding_middleware() -> PublicProfileOnboardingMiddleware:
    return PublicProfileOnboardingMiddleware(get_response=lambda request: "ok")
