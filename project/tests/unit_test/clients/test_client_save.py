from unittest.mock import patch

from clients.models import Client


def test_save_assigns_secret_when_blank(mocker) -> None:
    client = Client(name="blank-secret", domain="https://example.com")
    assert not client.secret

    with patch("django.db.models.Model.save"):
        client.save()

    assert client.secret
    assert len(client.secret) > 0


def test_save_preserves_provided_secret(mocker) -> None:
    client = Client(
        name="provided-secret",
        domain="https://example.com",
        secret="my-custom-secret",
    )

    with patch("django.db.models.Model.save"):
        client.save()

    assert client.secret == "my-custom-secret"


def test_generate_secret_returns_unique_values() -> None:
    secret_one = Client.generate_secret()
    secret_two = Client.generate_secret()

    assert secret_one
    assert secret_two
    assert secret_one != secret_two
