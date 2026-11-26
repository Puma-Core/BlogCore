from profiles.models import (
    SocialNetworkConfig,
    SocialNetworkInstance,
    VariableInstance,
)

from tests.unit_test.functions._variable import _variable


class _FakeUser:
    def __init__(self, username: str = "test-user") -> None:
        self.id = 1  # type: ignore[attr-defined]
        self.username = username

    def __str__(self) -> str:
        return self.username


def _build_user():
    return _FakeUser()


def _build_config(**overrides) -> SocialNetworkConfig:
    defaults = {
        "name": "Example",
        "template_url": "https://example.test/{username}",
        "icon_url": "https://example.test/icon.svg",
    }
    defaults.update(overrides)
    config = SocialNetworkConfig(**defaults)
    config.id = 1  # type: ignore[attr-defined]
    return config


def _build_parent(
    user=None,
    config: SocialNetworkConfig | None = None,
    *,
    pk: int | None = 1,
) -> SocialNetworkInstance:
    if user is None:
        user = _build_user()
    if config is None:
        config = _build_config()
    parent = SocialNetworkInstance(config=config)
    parent.author_id = user.id  # type: ignore[attr-defined]
    parent._state.fields_cache["author"] = user
    if pk is not None:
        parent.id = pk  # type: ignore[attr-defined]
    return parent


def _build_variable_instance(
    *,
    value: str = "test_user",
    variable=None,
    parent: SocialNetworkInstance | None = None,
    pk: int | None = None,
) -> VariableInstance:
    if variable is None:
        variable = _variable()
        variable.id = 1  # type: ignore[attr-defined]
    if parent is None:
        parent = _build_parent()
    return VariableInstance(
        pk=pk,
        social_network_instance=parent,
        variable=variable,
        value=value,
    )
