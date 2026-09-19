from clients.models import Client
from tests.unit_test.functions._mock_manager import mock_relation_manager


def mock_client_permissions(mocker, exists_return_value=True):
    mock_manager = mock_relation_manager(mocker, exists_return_value)
    mocker.patch.object(
        Client,
        "permissions",
        new_callable=mocker.PropertyMock,
        return_value=mock_manager,
    )
    return mock_manager


def mock_client_groups(mocker, exists_return_value=True):
    mock_manager = mock_relation_manager(mocker, exists_return_value)
    mocker.patch.object(
        Client,
        "groups",
        new_callable=mocker.PropertyMock,
        return_value=mock_manager,
    )
    return mock_manager
