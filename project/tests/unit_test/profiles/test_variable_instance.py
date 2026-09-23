import pytest
from django.core.exceptions import ValidationError
from django.db import models as django_models
from tests.unit_test.functions._social_network import (
    _build_parent,
    _build_user,
    _build_variable_instance,
)

from profiles.models import VariableInstance


def test_owner_returns_parent_social_network_instance_author() -> None:
    user = _build_user()
    parent = _build_parent(user=user)
    instance = _build_variable_instance(parent=parent)

    assert instance.owner is user


def test_clean_accepts_value_matching_regex_for_new_instance() -> None:
    instance = _build_variable_instance(value="test_user")

    instance.clean()


def test_clean_rejects_value_not_matching_regex_for_new_instance() -> None:
    instance = _build_variable_instance(value="test user")

    with pytest.raises(ValidationError) as exc_info:
        instance.clean()

    assert "value" in exc_info.value.message_dict


def test_value_validation_skips_a_variable_instance_without_variable() -> None:
    instance = VariableInstance(value="invalid value")

    instance._ensure_value_matches_regex()


def test_clean_rejects_modification_of_archived_instance(mocker) -> None:
    mock_objects = mocker.patch.object(VariableInstance, "objects")
    mock_objects.filter.return_value.values_list.return_value.first.return_value = True

    instance = _build_variable_instance(pk=1)

    with pytest.raises(ValidationError, match="Archived"):
        instance.clean()


def test_clean_rejects_variable_change(mocker) -> None:
    mock_objects = mocker.patch.object(VariableInstance, "objects")
    mock_objects.filter.return_value.values_list.return_value.first.return_value = False
    mock_objects.values.return_value.get.return_value = {
        "variable_id": 999,
        "social_network_instance_id": 1,
    }

    instance = _build_variable_instance(pk=1)

    with pytest.raises(ValidationError) as exc_info:
        instance.clean()

    assert "variable" in exc_info.value.message_dict


def test_clean_rejects_parent_change(mocker) -> None:
    mock_objects = mocker.patch.object(VariableInstance, "objects")
    mock_objects.filter.return_value.values_list.return_value.first.return_value = False
    mock_objects.values.return_value.get.return_value = {
        "variable_id": 1,
        "social_network_instance_id": 999,
    }

    instance = _build_variable_instance(pk=1)

    with pytest.raises(ValidationError) as exc_info:
        instance.clean()

    assert "social_network_instance" in exc_info.value.message_dict


def test_clean_accepts_value_only_change(mocker) -> None:
    mock_objects = mocker.patch.object(VariableInstance, "objects")
    mock_objects.filter.return_value.values_list.return_value.first.return_value = False
    mock_objects.values.return_value.get.return_value = {
        "variable_id": 1,
        "social_network_instance_id": 1,
    }

    instance = _build_variable_instance(pk=1, value="another_user")

    instance.clean()


def test_save_persists_changes(mocker) -> None:
    mock_save = mocker.patch.object(django_models.Model, "save")

    instance = _build_variable_instance()

    instance.save()

    mock_save.assert_called_once()


def test_save_rejects_modification_of_archived_instance(mocker) -> None:
    mock_objects = mocker.patch.object(VariableInstance, "objects")
    mock_objects.filter.return_value.values_list.return_value.first.return_value = True

    instance = _build_variable_instance(pk=1)

    with pytest.raises(ValidationError, match="Archived"):
        instance.save()


def test_save_persists_when_existing_instance_identity_is_preserved(
    mocker,
) -> None:
    mock_objects = mocker.patch.object(VariableInstance, "objects")
    mock_objects.filter.return_value.values_list.return_value.first.return_value = False
    mock_objects.values.return_value.get.return_value = {
        "variable_id": 1,
        "social_network_instance_id": 1,
    }
    mock_super_save = mocker.patch.object(django_models.Model, "save")

    instance = _build_variable_instance(pk=1, value="another_user")

    instance.save()

    mock_objects.values.assert_called_once()
    mock_super_save.assert_called_once()


def test_archive_marks_instance_as_archived_and_persists_only_that_field(
    mocker,
) -> None:
    mock_save = mocker.patch.object(django_models.Model, "save")
    instance = _build_variable_instance()

    instance.archive()

    assert instance.archived is True
    mock_save.assert_called_once_with(update_fields=["archived"])


def test_archive_does_not_query_database_when_never_persisted(mocker) -> None:
    mock_objects = mocker.patch.object(VariableInstance, "objects")
    mock_save = mocker.patch.object(django_models.Model, "save")

    instance = _build_variable_instance(pk=None)

    instance.archive()

    mock_objects.values.assert_not_called()
    mock_save.assert_called_once_with(update_fields=["archived"])


def test_delete_raises_protected_error_with_no_objects_when_unsaved() -> None:
    instance = _build_variable_instance(pk=None)
    instance.archived = True

    with pytest.raises(django_models.ProtectedError) as exc_info:
        instance.delete()

    assert exc_info.value.protected_objects == set()


def test_delete_reports_the_archived_persisted_instance() -> None:
    instance = _build_variable_instance(pk=1)
    instance.archived = True

    with pytest.raises(django_models.ProtectedError) as exc_info:
        instance.delete()

    assert exc_info.value.protected_objects == {instance}


def test_delete_protects_a_persisted_archived_instance() -> None:
    instance = _build_variable_instance(pk=1)
    instance.archived = True

    with pytest.raises(django_models.ProtectedError) as exc_info:
        instance.delete()

    assert exc_info.value.protected_objects == {instance}


def test_delete_protects_an_active_persisted_instance() -> None:
    instance = _build_variable_instance(pk=1)
    instance.archived = False

    with pytest.raises(django_models.ProtectedError) as exc_info:
        instance.delete()

    assert exc_info.value.protected_objects == {instance}


def test_str_returns_variable_and_value() -> None:
    instance = _build_variable_instance(value="test_user")

    assert str(instance) == "username=test_user"
