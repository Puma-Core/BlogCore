from clients.models import Client


def mock_client_with_id(client_factory) -> Client:
    client = client_factory()
    client.id = 1
    return client
