import pytest
from django.core.exceptions import ValidationError
from unittest.mock import MagicMock

from profiles.models import SocialNetworkConfig

from tests.unit_test.functions._social_network import _build_config
from tests.unit_test.functions._variable import _variable


def test_str_returns_name() -> None:
    config = _build_config(name="GitHub")

    assert str(config) == "GitHub"


def test_config_stores_constructor_attributes() -> None:
    config = _build_config(
        name="GitHub",
        template_url="https://github.com/{username}",
        icon_url="https://example.test/github.svg",
    )

    assert config.name == "GitHub"
    assert config.template_url == "https://github.com/{username}"
    assert config.icon_url == "https://example.test/github.svg"


def test_config_archived_defaults_to_false() -> None:
    config = _build_config()

    assert config.archived is False


def test_config_clean_accepts_template_with_associated_variables(
    mocker,
) -> None:
    variable = _variable(identifier="username")
    config = _build_config(template_url="https://example.test/{username}")
    mocker.patch.object(
        SocialNetworkConfig, "_associated_variables", return_value=[variable]
    )

    config.clean()


def test_config_clean_accepts_template_without_placeholders(mocker) -> None:
    config = _build_config(template_url="https://example.test/static")
    mocker.patch.object(
        SocialNetworkConfig, "_associated_variables", return_value=[]
    )

    config.clean()


def test_config_clean_rejects_template_with_unknown_variable(mocker) -> None:
    variable = _variable(identifier="username")
    config = _build_config(template_url="https://example.test/{missing}")
    mocker.patch.object(
        SocialNetworkConfig, "_associated_variables", return_value=[variable]
    )

    with pytest.raises(ValidationError) as exc_info:
        config.clean()

    assert "template_url" in exc_info.value.message_dict


def test_config_clean_rejects_template_with_any_unknown_variable(mocker) -> None:
    username = _variable(identifier="username")
    config = _build_config(template_url="https://example.test/{username}/{repo}")
    mocker.patch.object(
        SocialNetworkConfig, "_associated_variables", return_value=[username]
    )

    with pytest.raises(ValidationError) as exc_info:
        config.clean()

    assert "template_url" in exc_info.value.message_dict


def test_config_clean_rejects_template_with_no_associated_variables(
    mocker,
) -> None:
    config = _build_config(template_url="https://example.test/{username}")
    mocker.patch.object(
        SocialNetworkConfig, "_associated_variables", return_value=[]
    )

    with pytest.raises(ValidationError) as exc_info:
        config.clean()

    assert "template_url" in exc_info.value.message_dict


def test_config_extracts_all_template_placeholders() -> None:
    config = _build_config(
        template_url="https://example.test/{username}/{repo}"
    )

    assert sorted(config._template_placeholders()) == ["repo", "username"]


def test_associated_variables_delegates_to_m2m_manager(mocker) -> None:
    config = _build_config()
    expected = ["var1", "var2"]
    mock_manager = MagicMock()
    mock_manager.all.return_value = expected
    mocker.patch.object(SocialNetworkConfig, "variables", new=mock_manager)

    assert config._associated_variables() == expected