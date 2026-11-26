from django.contrib import admin

from clients.admin import ClientAdmin, ClientAdminForm
from clients.models import Client
from tests.unit_test.functions._request import _request


def test_client_admin_uses_custom_form() -> None:
    assert ClientAdmin.form is ClientAdminForm


def test_client_admin_list_display_does_not_include_secret() -> None:
    assert "secret" not in ClientAdmin.list_display


def test_client_admin_search_fields_include_name_and_domain() -> None:
    assert "name" in ClientAdmin.search_fields
    assert "domain" in ClientAdmin.search_fields


def test_client_admin_filters_include_is_active_and_groups() -> None:
    assert "is_active" in ClientAdmin.list_filter
    assert "groups" in ClientAdmin.list_filter


def test_client_admin_form_generates_secret_on_add() -> None:
    form = ClientAdminForm()

    assert "secret" in form.initial
    assert form.initial["secret"]
    assert len(form.initial["secret"]) > 0


def test_client_admin_form_preserves_secret_on_change(client_factory, mocker) -> None:
    client = client_factory(secret="existing-secret")
    client.pk = 1
    mocker.patch(
        "django.forms.models.model_to_dict",
        return_value={"secret": "existing-secret"},
    )
    form = ClientAdminForm(instance=client)

    assert form.initial["secret"] == "existing-secret"


def test_client_admin_get_fields_includes_secret_on_add() -> None:
    client_admin = ClientAdmin(Client, admin.site)
    request = _request()

    fields = client_admin.get_fields(request, None)

    assert "secret" in fields


def test_client_admin_get_fields_excludes_secret_on_change(client_factory) -> None:
    client = client_factory()
    client.pk = 1
    client_admin = ClientAdmin(Client, admin.site)
    request = _request()

    fields = client_admin.get_fields(request, client)

    assert "secret" not in fields
