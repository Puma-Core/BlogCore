import pytest

from django.contrib import admin

from profiles.admin import VariableAdmin
from profiles.models import Variable

from tests.unit_test.functions._request import _request


@pytest.fixture
def variable_admin() -> VariableAdmin:
    return VariableAdmin(Variable, admin.site)


def test_variable_is_registered_in_default_admin_site() -> None:
    assert Variable in admin.site._registry
    assert isinstance(admin.site._registry[Variable], VariableAdmin)


def test_admin_lists_identifier_label_and_description(variable_admin) -> None:
    assert variable_admin.list_display == ("identifier", "label", "description")


def test_admin_search_includes_identifier_label_and_description(
    variable_admin,
) -> None:
    assert "identifier" in variable_admin.search_fields
    assert "label" in variable_admin.search_fields
    assert "description" in variable_admin.search_fields


def test_admin_orders_by_identifier(variable_admin) -> None:
    assert variable_admin.ordering == ("identifier",)


def test_staff_with_add_permission_can_add(variable_admin) -> None:
    request = _request(is_staff=True, has_perm=True)

    assert variable_admin.has_add_permission(request) is True


def test_non_staff_cannot_add(variable_admin) -> None:
    request = _request(is_staff=False, has_perm=False)

    assert variable_admin.has_add_permission(request) is False


def test_staff_without_add_permission_cannot_add(variable_admin) -> None:
    request = _request(is_staff=True, has_perm=False)

    assert variable_admin.has_add_permission(request) is False


def test_staff_with_change_permission_can_change(variable_admin) -> None:
    request = _request(is_staff=True, has_perm=True)

    assert variable_admin.has_change_permission(request) is True


def test_non_staff_cannot_change(variable_admin) -> None:
    request = _request(is_staff=False, has_perm=False)

    assert variable_admin.has_change_permission(request) is False


def test_staff_with_delete_permission_can_delete(variable_admin) -> None:
    request = _request(is_staff=True, has_perm=True)

    assert variable_admin.has_delete_permission(request) is True


def test_non_staff_cannot_delete(variable_admin) -> None:
    request = _request(is_staff=False, has_perm=False)

    assert variable_admin.has_delete_permission(request) is False


def test_staff_with_view_permission_can_view(variable_admin) -> None:
    request = _request(is_staff=True, has_perm=True)

    assert variable_admin.has_view_permission(request) is True


def test_non_staff_cannot_view(variable_admin) -> None:
    request = _request(is_staff=False, has_perm=False)

    assert variable_admin.has_view_permission(request) is False
