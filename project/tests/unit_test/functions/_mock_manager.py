def mock_relation_manager(mocker, exists_return_value=True):
    mock_manager = mocker.MagicMock()
    mock_manager.filter.return_value.exists.return_value = exists_return_value
    return mock_manager
