import pytest
from django import forms as django_forms
from django.contrib import admin

from profiles.admin import SocialNetworkConfigAdmin
from profiles.forms.social_network_config import SocialNetworkConfigForm
from profiles.models import SocialNetworkConfig

from tests.unit_test.functions._request import _request
from tests.unit_test.functions._variable import _variable


def test_social_network_config_is_registered_in_default_admin_site() -> None:
    assert SocialNetworkConfig in admin.site._registry
    assert isinstance(admin.site._registry[SocialNetworkConfig], SocialNetworkConfigAdmin)


def test_admin_lists_name_template_url_and_icon_url(
    social_network_config_admin,
) -> None:
    assert social_network_config_admin.list_display == (
        "name",
        "template_url",
        "icon_url",
    )


def test_admin_search_includes_name(social_network_config_admin) -> None:
    assert "name" in social_network_config_admin.search_fields


def test_admin_orders_by_name(social_network_config_admin) -> None:
    assert social_network_config_admin.ordering == ("name",)


def test_admin_uses_horizontal_filter_for_variables(
    social_network_config_admin,
) -> None:
    assert social_network_config_admin.filter_horizontal == ("variables",)


def test_staff_with_add_permission_can_add(social_network_config_admin) -> None:
    request = _request(is_staff=True, has_perm=True)

    assert social_network_config_admin.has_add_permission(request) is True


def test_non_staff_cannot_add(social_network_config_admin) -> None:
    request = _request(is_staff=False, has_perm=False)

    assert social_network_config_admin.has_add_permission(request) is False


def test_staff_without_add_permission_cannot_add(
    social_network_config_admin,
) -> None:
    request = _request(is_staff=True, has_perm=False)

    assert social_network_config_admin.has_add_permission(request) is False


def test_staff_with_change_permission_can_change(
    social_network_config_admin,
) -> None:
    request = _request(is_staff=True, has_perm=True)

    assert social_network_config_admin.has_change_permission(request) is True


def test_non_staff_cannot_change(social_network_config_admin) -> None:
    request = _request(is_staff=False, has_perm=False)

    assert social_network_config_admin.has_change_permission(request) is False


def test_staff_with_delete_permission_can_delete(
    social_network_config_admin,
) -> None:
    request = _request(is_staff=True, has_perm=True)

    assert social_network_config_admin.has_delete_permission(request) is True


def test_non_staff_cannot_delete(social_network_config_admin) -> None:
    request = _request(is_staff=False, has_perm=False)

    assert social_network_config_admin.has_delete_permission(request) is False


def test_staff_with_view_permission_can_view(
    social_network_config_admin,
) -> None:
    request = _request(is_staff=True, has_perm=True)

    assert social_network_config_admin.has_view_permission(request) is True


def test_non_staff_cannot_view(social_network_config_admin) -> None:
    request = _request(is_staff=False, has_perm=False)

    assert social_network_config_admin.has_view_permission(request) is False


def test_form_accepts_template_with_associated_variable() -> None:
    username = _variable(identifier="username")
    form = SocialNetworkConfigForm()
    form.cleaned_data = {
        "name": "GitHub",
        "template_url": "https://example.test/{username}",
        "icon_url": "https://example.test/icon.svg",
        "variables": [username],
    }

    result = form.clean()

    assert result["template_url"] == "https://example.test/{username}"


def test_form_accepts_template_without_placeholders() -> None:
    form = SocialNetworkConfigForm()
    form.cleaned_data = {
        "name": "Static",
        "template_url": "https://example.test/static",
        "icon_url": "https://example.test/icon.svg",
        "variables": [],
    }

    form.clean()


def test_form_rejects_template_referencing_unknown_variable() -> None:
    form = SocialNetworkConfigForm()
    form.cleaned_data = {
        "name": "GitHub",
        "template_url": "https://example.test/{missing}",
        "icon_url": "https://example.test/icon.svg",
        "variables": [],
    }

    with pytest.raises(django_forms.ValidationError) as exc_info:
        form.clean()

    assert "template_url" in exc_info.value.message_dict


def test_form_rejects_template_when_any_placeholder_is_unassociated() -> None:
    username = _variable(identifier="username")
    form = SocialNetworkConfigForm()
    form.cleaned_data = {
        "name": "GitHub",
        "template_url": "https://example.test/{username}/{repo}",
        "icon_url": "https://example.test/icon.svg",
        "variables": [username],
    }

    with pytest.raises(django_forms.ValidationError) as exc_info:
        form.clean()

    assert "template_url" in exc_info.value.message_dict