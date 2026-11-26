from typing import Any

import pytest

from clients.models import Client


@pytest.fixture
def client_factory():
    def _client(**overrides: Any) -> Client:
        defaults = {
            "name": "test-client",
            "domain": "https://example.com",
        }
        defaults.update(overrides)
        return Client(**defaults)

    return _client
