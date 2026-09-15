from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ValidationError
from django.db import models as django_models
from tests.unit_test.functions._social_network import (
    _build_config,
    _build_parent,
)
from tests.unit_test.functions._variable import _variable

from profiles.models import SocialNetworkConfig, SocialNetworkInstance


def test_str_returns_config_name_and_author() -> None:
    parent = _build_parent()

    assert str(parent) == "Example (test-user)"


def test_instance_stores_constructor_attributes() -> None:
    config = _build_config(name="GitHub")
    parent = _build_parent(config=config)

    assert parent.config is config
    assert parent.archived is False


def test_instance_archived_defaults_to_false() -> None:
    parent = _build_parent(pk=None)

    assert parent.archived is False


def test_instance_save_persists_new_instance(mocker) -> None:
    mock_super_save = mocker.patch.object(django_models.Model, "save")

    parent = _build_parent(pk=None)

    parent.save()

    mock_super_save.assert_called_once()


def test_instance_save_rejects_modification_when_archived(mocker) -> None:
    mock_objects = mocker.patch.object(SocialNetworkInstance, "objects")
    mock_objects.filter.return_value.values.return_value.first.return_value = {
        "archived": True,
        "author_id": 1,
    }

    parent = _build_parent()
    parent.author_id = 1  # type: ignore[attr-defined]

    with pytest.raises(ValidationError, match="Archived"):
        parent.save()


def test_instance_save_rejects_author_change(mocker) -> None:
    mock_objects = mocker.patch.object(SocialNetworkInstance, "objects")
    mock_objects.filter.return_value.values.return_value.first.return_value = {
        "archived": False,
        "author_id": 999,
    }

    parent = _build_parent()
    parent.author_id = 1  # type: ignore[attr-defined]

    with pytest.raises(ValidationError) as exc_info:
        parent.save()

    assert "author" in exc_info.value.message_dict


def test_instance_save_preserves_author(mocker) -> None:
    mock_objects = mocker.patch.object(SocialNetworkInstance, "objects")
    mock_objects.filter.return_value.values.return_value.first.return_value = {
        "archived": False,
        "author_id": 1,
    }
    mock_super_save = mocker.patch.object(django_models.Model, "save")

    parent = _build_parent()
    parent.author_id = 1  # type: ignore[attr-defined]

    parent.save()

    mock_super_save.assert_called_once()


def test_instance_clean_accepts_variable_defined_by_config(mocker) -> None:
    variable = _variable(identifier="username")
    config = _build_config(template_url="https://example.test/{username}")
    parent = _build_parent(config=config)
    mocker.patch.object(
        SocialNetworkConfig, "_associated_variables", return_value=[variable]
    )
    parent._iter_variable_instances = MagicMock(return_value=[])  # type: ignore[method-assign]

    parent.clean()


def test_instance_clean_rejects_variable_not_defined_by_config(mocker) -> None:
    username = _variable(identifier="username")
    other = _variable(identifier="phone")
    config = _build_config(template_url="https://example.test/{username}")
    parent = _build_parent(config=config)
    mocker.patch.object(
        SocialNetworkConfig, "_associated_variables", return_value=[username]
    )

    bad_variable_instance = MagicMock()
    bad_variable_instance.variable = other
    parent._iter_variable_instances = MagicMock(  # type: ignore[method-assign]
        return_value=[bad_variable_instance]
    )

    with pytest.raises(ValidationError) as exc_info:
        parent.clean()

    assert "variable_instances" in exc_info.value.message_dict


def test_instance_url_builds_from_template_and_active_variable_values(
    mocker,
) -> None:
    username = _variable(identifier="username")
    config = _build_config(template_url="https://example.test/{username}")
    parent = _build_parent(config=config)
    mocker.patch.object(
        SocialNetworkConfig, "_associated_variables", return_value=[username]
    )

    value_instance = MagicMock()
    value_instance.variable = username
    value_instance.value = "octocat"
    parent._active_variable_instances = MagicMock(  # type: ignore[method-assign]
        return_value=[value_instance]
    )

    assert parent.url == "https://example.test/octocat"


def test_instance_url_returns_none_when_placeholder_has_no_value(mocker) -> None:
    username = _variable(identifier="username")
    repo = _variable(identifier="repo")
    config = _build_config(template_url="https://example.test/{username}/{repo}")
    parent = _build_parent(config=config)
    mocker.patch.object(
        SocialNetworkConfig,
        "_associated_variables",
        return_value=[username, repo],
    )

    value_instance = MagicMock()
    value_instance.variable = username
    value_instance.value = "octocat"
    parent._active_variable_instances = MagicMock(  # type: ignore[method-assign]
        return_value=[value_instance]
    )

    assert parent.url is None


def test_instance_url_ignores_archived_variable_values(mocker) -> None:
    username = _variable(identifier="username")
    config = _build_config(template_url="https://example.test/{username}")
    parent = _build_parent(config=config)
    mocker.patch.object(
        SocialNetworkConfig, "_associated_variables", return_value=[username]
    )

    parent._active_variable_instances = MagicMock(return_value=[])  # type: ignore[method-assign]

    assert parent.url is None


def test_instance_url_returns_template_when_no_placeholders() -> None:
    config = _build_config(template_url="https://example.test/static")
    parent = _build_parent(config=config)

    assert parent.url == "https://example.test/static"


def test_instance_icon_url_returns_config_icon_url() -> None:
    config = _build_config(icon_url="https://example.test/icon.svg")
    parent = _build_parent(config=config)

    assert parent.icon_url == "https://example.test/icon.svg"


def test_instance_archive_marks_as_archived_and_persists_only_that_field(
    mocker,
) -> None:
    mock_objects = mocker.patch.object(SocialNetworkInstance, "objects")
    mock_objects.filter.return_value.values.return_value.first.return_value = {
        "archived": False,
        "author_id": 1,
    }
    mock_super_save = mocker.patch.object(django_models.Model, "save")
    parent = _build_parent()
    parent.author_id = 1  # type: ignore[attr-defined]

    parent.archive()

    assert parent.archived is True
    mock_super_save.assert_called_once_with(update_fields=["archived"])


def test_instance_delete_raises_protected_error_when_archived() -> None:
    parent = _build_parent(pk=None)
    parent.archived = True

    with pytest.raises(django_models.ProtectedError):
        parent.delete()


def test_instance_delete_protects_a_persisted_archived_instance() -> None:
    parent = _build_parent()
    parent.archived = True

    with pytest.raises(django_models.ProtectedError) as exc_info:
        parent.delete()

    assert exc_info.value.protected_objects == {parent}


def test_instance_delete_calls_super_when_not_archived(mocker) -> None:
    mock_super_delete = mocker.patch.object(django_models.Model, "delete")
    parent = _build_parent(pk=None)
    parent.archived = False

    parent.delete()

    mock_super_delete.assert_called_once()


def test_instance_clean_skips_config_check_when_config_id_is_none() -> None:
    parent = _build_parent()
    parent.config = None
    parent._iter_variable_instances = MagicMock()  # type: ignore[method-assign]

    parent.clean()

    parent._iter_variable_instances.assert_not_called()


def test_load_state_returns_none_when_pk_is_none() -> None:
    parent = _build_parent(pk=None)

    assert parent._load_state() is None


def test_ensure_not_archived_returns_when_state_is_none() -> None:
    parent = _build_parent(pk=None)

    parent._ensure_not_archived(None)


def test_ensure_author_preserved_returns_when_state_is_none() -> None:
    parent = _build_parent(pk=None)

    parent._ensure_author_preserved(None)


def test_active_variable_instances_delegates_to_reverse_manager(mocker) -> None:
    parent = _build_parent(pk=None)
    expected = ["vi1", "vi2"]
    mock_manager = MagicMock()
    mock_manager.filter.return_value = expected
    mocker.patch.object(
        SocialNetworkInstance, "variable_instances", new=mock_manager
    )

    assert parent._active_variable_instances() == expected


def test_iter_variable_instances_delegates_to_reverse_manager(mocker) -> None:
    parent = _build_parent(pk=None)
    expected = ["vi1", "vi2"]
    mock_manager = MagicMock()
    mock_manager.all.return_value = expected
    mocker.patch.object(
        SocialNetworkInstance, "variable_instances", new=mock_manager
    )

    assert parent._iter_variable_instances() == expected
