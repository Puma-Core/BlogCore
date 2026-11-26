from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError
from django.db import models as django_models
from django.urls import Resolver404, reverse

from profiles.admin.public_profile import PublicProfileForm
from profiles.middleware import PublicProfileOnboardingMiddleware
from profiles.models import PublicProfile
from tests.factories import create_public_profile, create_user
from tests.unit_test.functions._request import _request


# ---------------------------------------------------------------------------
# PublicProfileOnboardingMiddleware
# ---------------------------------------------------------------------------


def test_call_redirects_when_onboarding_required(onboarding_middleware):
    request = _request(is_authenticated=True, is_staff=True)
    response = onboarding_middleware(request)

    assert response.status_code == 302
    assert response["Location"] == reverse("admin:profiles_publicprofile_add")


def test_call_continues_when_onboarding_not_required(onboarding_middleware):
    request = _request(path="/admin/login/", is_authenticated=False)

    assert onboarding_middleware(request) == "ok"


def test_must_onboard_false_for_non_admin_path(onboarding_middleware):
    request = _request(path="/", is_authenticated=True, is_staff=True)

    assert onboarding_middleware._must_onboard(request) is False


def test_must_onboard_false_for_anonymous_user(onboarding_middleware):
    request = _request(is_authenticated=False)

    assert onboarding_middleware._must_onboard(request) is False


def test_must_onboard_false_for_non_staff_user(onboarding_middleware):
    request = _request(is_authenticated=True, is_staff=False)

    assert onboarding_middleware._must_onboard(request) is False


def test_must_onboard_false_for_exempt_url(onboarding_middleware):
    request = _request(path="/admin/login/", is_authenticated=True, is_staff=True)

    assert onboarding_middleware._must_onboard(request) is False


def test_must_onboard_false_when_profile_exists(onboarding_middleware):
    request = _request(is_authenticated=True, is_staff=True, has_profile=True)

    assert onboarding_middleware._must_onboard(request) is False


def test_must_onboard_true_when_profile_missing(onboarding_middleware):
    request = _request(
        path="/admin/profiles/publicprofile/",
        is_authenticated=True,
        is_staff=True,
    )

    assert onboarding_middleware._must_onboard(request) is True


@pytest.mark.parametrize(
    "path,expected",
    [
        ("/admin/login/", True),
        ("/admin/logout/", True),
        ("/admin/password_change/", True),
        ("/admin/password_change/done/", True),
        ("/admin/profiles/publicprofile/add/", True),
        ("/admin/profiles/publicprofile/", False),
        ("/admin/auth/group/", False),
    ],
)
def test_is_exempt_for_admin_urls(onboarding_middleware, path, expected):
    request = _request(path=path)

    assert onboarding_middleware._is_exempt(request) is expected


def test_is_exempt_false_for_unresolvable_url(onboarding_middleware, mocker):
    request = _request(path="/admin/not-a-real-url/")
    resolve_mock = mocker.patch("profiles.middleware.resolve")
    resolve_mock.side_effect = Resolver404

    assert onboarding_middleware._is_exempt(request) is False


# ---------------------------------------------------------------------------
# PublicProfileForm
# ---------------------------------------------------------------------------


def test_form_omits_user_field():
    assert tuple(PublicProfileForm.base_fields) == (
        "public_username",
        "first_name",
        "last_name",
        "title",
        "subtitle",
        "specialty",
        "short_description",
        "photo_url",
    )


def test_form_accepts_user_keyword_only():
    user = create_user(pk=1)
    form = PublicProfileForm(user=user)

    assert form.user is user


def test_form_prefills_from_user():
    user = create_user(pk=1, username="jdoe", first_name="John", last_name="Doe")
    form = PublicProfileForm(user=user)

    assert form.fields["public_username"].initial == "jdoe"
    assert form.fields["first_name"].initial == "John"
    assert form.fields["last_name"].initial == "Doe"


def test_form_does_not_prefill_when_editing():
    user = create_user(pk=1, username="jdoe")
    profile = create_public_profile(
        pk=1,
        user=user,
        public_username="existing",
        first_name="Existing",
        last_name="Profile",
    )
    form = PublicProfileForm(instance=profile, user=user)

    assert form.initial.get("public_username") == "existing"


# ---------------------------------------------------------------------------
# PublicProfileAdmin
# ---------------------------------------------------------------------------


def test_get_form_binds_user_to_form_class(public_profile_admin):
    request = _request(is_authenticated=True, is_staff=True)
    form_class = public_profile_admin.get_form(request)
    form = form_class()

    assert form.user is request.user


def test_get_queryset_returns_empty_when_request_is_none(public_profile_admin):
    assert list(public_profile_admin.get_queryset(None)) == []


def test_get_queryset_filters_by_request_user(public_profile_admin, mocker):
    queryset = mocker.MagicMock()
    mocker.patch.object(
        public_profile_admin.__class__.__bases__[0],
        "get_queryset",
        return_value=queryset,
    )
    request = _request(is_authenticated=True, is_staff=True)

    public_profile_admin.get_queryset(request)

    queryset.filter.assert_called_once_with(user_id=request.user.id)


def test_has_module_permission_only_for_staff(public_profile_admin):
    assert public_profile_admin.has_module_permission(_request(is_staff=True)) is True
    assert public_profile_admin.has_module_permission(_request(is_staff=False)) is False
    assert public_profile_admin.has_module_permission(_request(is_authenticated=False)) is False
    assert public_profile_admin.has_module_permission(None) is False


def test_has_add_permission_for_staff_without_profile(public_profile_admin, mocker):
    mocker.patch.object(
        PublicProfile.objects, "filter", return_value=Mock(exists=Mock(return_value=False))
    )
    request = _request(is_authenticated=True, is_staff=True)

    assert public_profile_admin.has_add_permission(request) is True


def test_has_add_permission_denied_when_profile_exists(public_profile_admin, mocker):
    mocker.patch.object(
        PublicProfile.objects, "filter", return_value=Mock(exists=Mock(return_value=True))
    )
    request = _request(is_authenticated=True, is_staff=True)

    assert public_profile_admin.has_add_permission(request) is False


def test_has_add_permission_denied_for_non_staff_or_anonymous(public_profile_admin):
    assert public_profile_admin.has_add_permission(_request(is_staff=False)) is False
    assert public_profile_admin.has_add_permission(_request(is_authenticated=False)) is False
    assert public_profile_admin.has_add_permission(None) is False


def test_has_change_permission_allows_owner(public_profile_admin):
    own_profile = PublicProfile(user_id=1)
    other_profile = PublicProfile(user_id=2)
    request = _request(is_authenticated=True, is_staff=True)

    assert public_profile_admin.has_change_permission(request, own_profile) is True
    assert public_profile_admin.has_change_permission(request, other_profile) is False


def test_has_change_permission_without_object_uses_profile_existence(public_profile_admin, mocker):
    mocker.patch.object(
        PublicProfile.objects, "filter", return_value=Mock(exists=Mock(return_value=True))
    )
    request = _request(is_authenticated=True, is_staff=True)

    assert public_profile_admin.has_change_permission(request) is True


def test_has_change_permission_denied_for_non_staff_or_anonymous(public_profile_admin):
    assert public_profile_admin.has_change_permission(_request(is_staff=False)) is False
    assert public_profile_admin.has_change_permission(_request(is_authenticated=False)) is False
    assert public_profile_admin.has_change_permission(None) is False


def test_save_model_assigns_request_user_on_creation(public_profile_admin, mocker):
    user = create_user(pk=1)
    request = _request(user=user)
    profile = PublicProfile()
    form = Mock()
    mocker.patch("django.db.models.Model.save")

    public_profile_admin.save_model(request, profile, form, change=False)

    assert profile.user is user


# ---------------------------------------------------------------------------
# Onboarding group
# ---------------------------------------------------------------------------


def test_onboarding_group_name_matches_settings():
    from django.conf import settings

    assert settings.PUBLIC_PROFILE_ONBOARDING_GROUP_NAME == "Public Profile Onboarding"


def test_migration_file_exists():
    import importlib

    migration_module = importlib.import_module("profiles.migrations.0004_onboarding_group")

    assert hasattr(migration_module, "create_onboarding_group")
    assert hasattr(migration_module, "remove_onboarding_group")


# ---------------------------------------------------------------------------
# Ownership and groups
# ---------------------------------------------------------------------------


def test_public_profile_rejects_user_reassignment(mocker):
    original = create_user(pk=1)
    other = create_user(pk=2)
    profile = PublicProfile(pk=1, user=original)
    profile.user = other

    mocker.patch.object(
        PublicProfile.objects,
        "filter",
        return_value=Mock(
            values_list=Mock(return_value=Mock(first=Mock(return_value=1)))
        ),
    )
    mocker.patch("django.db.models.Model.save")

    with pytest.raises(ValidationError, match="cannot change"):
        profile.save()


def test_user_cannot_create_profile_for_another_user(public_profile_admin, mocker):
    staff_user = create_user(pk=1)
    other_user = create_user(pk=2)
    request = _request(user=staff_user)
    profile = PublicProfile()
    form = Mock()
    mocker.patch("django.db.models.Model.save")

    public_profile_admin.save_model(request, profile, form, change=False)

    assert profile.user is staff_user
    assert profile.user is not other_user
