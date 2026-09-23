import pytest
from django.core.exceptions import ValidationError

from clients.models import Client
from clients.validators import validate_domains
from tests.unit_test.mocks.clients.mock_client import mock_client_with_id
from tests.unit_test.mocks.clients.mock_permissions import (
    mock_client_groups,
    mock_client_permissions,
)


# Model metadata tests


def test_client_str_returns_name(client_factory) -> None:
    client = client_factory(name="ACME")

    assert str(client) == "ACME"


def test_client_name_field_is_unique() -> None:
    field = Client._meta.get_field("name")

    assert field.unique is True


def test_client_secret_field_is_unique_and_blank() -> None:
    field = Client._meta.get_field("secret")

    assert field.unique is True
    assert field.blank is True


# Secret generation tests


def test_client_generate_secret_returns_non_empty_token() -> None:
    secret = Client.generate_secret()

    assert secret
    assert len(secret) > 0


def test_client_preserves_provided_secret(client_factory) -> None:
    client = client_factory(secret="my-custom-secret")

    assert client.secret == "my-custom-secret"


# Domain validation tests


def test_validate_domains_accepts_valid_single_url() -> None:
    assert validate_domains("https://example.com") is None


def test_validate_domains_accepts_valid_multiple_urls() -> None:
    assert validate_domains("https://example.com,http://app.example.org") is None


def test_validate_domains_rejects_missing_protocol() -> None:
    with pytest.raises(ValidationError):
        validate_domains("example.com")


def test_validate_domains_rejects_empty_entry() -> None:
    with pytest.raises(ValidationError):
        validate_domains("https://example.com,")


def test_validate_domains_rejects_empty_value() -> None:
    with pytest.raises(ValidationError):
        validate_domains("")


# is_domain_allowed tests


def test_is_domain_allowed_returns_true_for_allowed_host(client_factory) -> None:
    client = client_factory(domain="https://example.com,http://app.example.org")

    assert client.is_domain_allowed("example.com") is True
    assert client.is_domain_allowed("app.example.org") is True


def test_is_domain_allowed_returns_false_for_unknown_host(client_factory) -> None:
    client = client_factory(domain="https://example.com")

    assert client.is_domain_allowed("evil.com") is False


# Permission helper tests using mocks to avoid database access


def test_has_perm_returns_true_for_direct_permission(client_factory, mocker) -> None:
    client = mock_client_with_id(client_factory)
    mock_client_permissions(mocker, exists_return_value=True)

    assert client.has_perm("some.permission") is True


def test_has_perm_returns_true_for_group_permission(client_factory, mocker) -> None:
    client = mock_client_with_id(client_factory)
    mock_client_permissions(mocker, exists_return_value=False)
    mock_client_groups(mocker, exists_return_value=True)

    assert client.has_perm("some.permission") is True


def test_has_perm_returns_false_for_missing_permission(client_factory, mocker) -> None:
    client = mock_client_with_id(client_factory)
    mock_client_permissions(mocker, exists_return_value=False)
    mock_client_groups(mocker, exists_return_value=False)

    assert client.has_perm("nonexistent.permission") is False


def test_has_module_perms_returns_true_for_direct_app_permission(client_factory, mocker) -> None:
    client = mock_client_with_id(client_factory)
    mock_client_permissions(mocker, exists_return_value=True)

    assert client.has_module_perms("auth") is True


def test_has_module_perms_returns_false_for_missing_app(client_factory, mocker) -> None:
    client = mock_client_with_id(client_factory)
    mock_client_permissions(mocker, exists_return_value=False)
    mock_client_groups(mocker, exists_return_value=False)

    assert client.has_module_perms("nonexistent") is False
