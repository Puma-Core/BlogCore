import pytest
from django.core.exceptions import ValidationError

from tests.unit_test.functions._variable import _variable


def test_variable_stores_constructor_attributes() -> None:
    variable = _variable(
        identifier="post_url",
        label="Post URL",
        description="Public post URL identifier",
        regex=r"[A-Za-z0-9-]+",
    )

    assert variable.identifier == "post_url"
    assert variable.label == "Post URL"
    assert variable.description == "Public post URL identifier"
    assert variable.regex == r"[A-Za-z0-9-]+"


def test_variable_str_returns_identifier() -> None:
    variable = _variable(identifier="post_url")

    assert str(variable) == "post_url"


def test_variable_matches_returns_true_for_full_match() -> None:
    variable = _variable(regex=r"[A-Za-z0-9_]+")

    assert variable.matches("test_user") is True


def test_variable_matches_returns_false_when_extra_characters_are_appended() -> None:
    variable = _variable(regex=r"[A-Za-z0-9_]+")

    assert variable.matches("test_user!") is False


def test_variable_matches_returns_false_when_disallowed_character_present() -> None:
    variable = _variable(regex=r"[A-Za-z0-9_]+")

    assert variable.matches("test user") is False
    assert variable.matches("test!") is False


def test_variable_matches_returns_false_for_empty_value() -> None:
    variable = _variable(regex=r"[A-Za-z0-9_]+")

    assert variable.matches("") is False


def test_variable_matches_returns_false_when_value_too_short() -> None:
    variable = _variable(regex=r"[A-Za-z0-9_]{3,}")

    assert variable.matches("ab") is False
    assert variable.matches("abc") is True


def test_variable_clean_accepts_compilable_regex() -> None:
    variable = _variable(regex=r"^\d{4}$")

    variable.clean()


def test_variable_clean_rejects_uncompilable_regex() -> None:
    variable = _variable(regex="[invalid")

    with pytest.raises(ValidationError) as exc_info:
        variable.clean()

    assert "regex" in exc_info.value.message_dict
