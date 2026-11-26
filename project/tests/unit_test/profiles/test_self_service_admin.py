from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models as django_models

from profiles.admin.public_profile import PublicProfileAdmin, PublicProfileForm
from profiles.models import PublicProfile
from tests.factories import create_user
from tests.unit_test.functions._request import _request


def test_public_profile_form_omits_user_field() -> None:
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


def test_public_profile_admin_exposes_module_only_to_staff(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    assert public_profile_admin.has_module_permission(_request(is_staff=True)) is True
    assert public_profile_admin.has_module_permission(_request(is_staff=False)) is False
    assert (
        public_profile_admin.has_module_permission(_request(is_authenticated=False))
        is False
    )
    assert public_profile_admin.has_module_permission(None) is False


def test_public_profile_admin_allows_add_when_profile_is_missing(
    mocker, public_profile_admin: PublicProfileAdmin
) -> None:
    mocker.patch.object(
        PublicProfile.objects, "filter", return_value=Mock(exists=Mock(return_value=False))
    )

    assert public_profile_admin.has_add_permission(_request()) is True


def test_public_profile_admin_denies_second_add(
    mocker, public_profile_admin: PublicProfileAdmin
) -> None:
    mocker.patch.object(
        PublicProfile.objects, "filter", return_value=Mock(exists=Mock(return_value=True))
    )

    assert public_profile_admin.has_add_permission(_request()) is False


def test_public_profile_admin_denies_add_for_non_staff(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    assert public_profile_admin.has_add_permission(_request(is_staff=False)) is False
    assert (
        public_profile_admin.has_add_permission(_request(is_authenticated=False))
        is False
    )
    assert public_profile_admin.has_add_permission(None) is False


def test_public_profile_admin_allows_only_owner_to_change(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    own_profile = PublicProfile(user_id=1)
    other_profile = PublicProfile(user_id=2)
    request = _request()

    assert public_profile_admin.has_change_permission(request, own_profile) is True
    assert public_profile_admin.has_change_permission(request, other_profile) is False
    assert public_profile_admin.has_view_permission(request, own_profile) is True
    assert public_profile_admin.has_view_permission(request, other_profile) is False
    assert public_profile_admin.has_delete_permission(request, own_profile) is False


def test_public_profile_admin_allows_change_without_object_when_profile_exists(
    mocker, public_profile_admin: PublicProfileAdmin
) -> None:
    mocker.patch.object(
        PublicProfile.objects, "filter", return_value=Mock(exists=Mock(return_value=True))
    )

    assert public_profile_admin.has_change_permission(_request()) is True


def test_public_profile_admin_denies_change_without_object_when_profile_missing(
    mocker, public_profile_admin: PublicProfileAdmin
) -> None:
    mocker.patch.object(
        PublicProfile.objects, "filter", return_value=Mock(exists=Mock(return_value=False))
    )

    assert public_profile_admin.has_change_permission(_request()) is False


def test_public_profile_admin_returns_empty_queryset_when_request_is_none(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    assert list(public_profile_admin.get_queryset(None)) == []


def test_public_profile_admin_denies_change_for_unauthenticated_request(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    assert (
        public_profile_admin.has_change_permission(_request(is_authenticated=False))
        is False
    )
    assert public_profile_admin.has_change_permission(_request(is_staff=False)) is False
    assert public_profile_admin.has_change_permission(None) is False


def test_public_profile_admin_filters_queryset_to_request_user(
    mocker, public_profile_admin: PublicProfileAdmin
) -> None:
    queryset = mocker.MagicMock()
    base_get_queryset = mocker.patch.object(
        admin.ModelAdmin, "get_queryset", return_value=queryset
    )
    request = _request()

    result = public_profile_admin.get_queryset(request)

    base_get_queryset.assert_called_once_with(request)
    queryset.filter.assert_called_once_with(user_id=request.user.id)
    assert result is queryset.filter.return_value


def test_public_profile_admin_assigns_request_user_when_creating(
    mocker, public_profile_admin: PublicProfileAdmin
) -> None:
    user = create_user(pk=1, username="profile-owner")
    request = _request(user=user)
    profile = PublicProfile()
    form = mocker.MagicMock(spec=forms.ModelForm)
    mocker.patch.object(django_models.Model, "save")

    public_profile_admin.save_model(request, profile, form, change=False)

    assert profile.user is request.user


def test_public_profile_rejects_user_reassignment(mocker) -> None:
    original = create_user(pk=1)
    other = create_user(pk=2)
    profile = PublicProfile(pk=1, user=original)
    profile.user = other

    mocker.patch.object(
        PublicProfile.objects, "filter", return_value=Mock(values_list=Mock(return_value=Mock(first=Mock(return_value=1))))
    )
    mocker.patch.object(django_models.Model, "save")

    with pytest.raises(ValidationError, match="cannot change"):
        profile.save()
