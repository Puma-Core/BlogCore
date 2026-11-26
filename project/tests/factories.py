from typing import Any

from django.contrib.auth import get_user_model


def create_user(**overrides: Any) -> Any:
    defaults = {
        "username": "test-user",
        "password": "test-password",
    }
    defaults.update(overrides)
    password = defaults.pop("password")
    user = get_user_model()(**defaults)
    user.set_password(password)
    return user


def create_variable(**overrides: Any) -> Any:
    from profiles.models import Variable

    defaults = {
        "identifier": "username",
        "label": "Username",
        "description": "Social network username",
        "regex": r"[A-Za-z0-9_]+",
    }
    defaults.update(overrides)
    return Variable(**defaults)


def create_social_network_config(**overrides: Any) -> Any:
    from profiles.models import SocialNetworkConfig

    variables = overrides.pop("variables", [])
    defaults = {
        "name": "Example",
        "template_url": "https://example.test/{username}",
        "icon_url": "https://example.test/icon.svg",
    }
    defaults.update(overrides)
    config = SocialNetworkConfig(**defaults)
    config._factory_variables = variables  # type: ignore[attr-defined]
    return config


def create_social_network_instance(**overrides: Any) -> Any:
    from profiles.models import SocialNetworkInstance

    defaults = {
        "author": create_user(),
        "config": create_social_network_config(),
    }
    defaults.update(overrides)
    return SocialNetworkInstance(**defaults)


def create_variable_instance(**overrides: Any) -> Any:
    from profiles.models import VariableInstance

    defaults = {
        "social_network_instance": create_social_network_instance(),
        "variable": create_variable(),
        "value": "test-user",
    }
    defaults.update(overrides)
    return VariableInstance(**defaults)


def create_public_profile(**overrides: Any) -> Any:
    from profiles.models import PublicProfile  # type: ignore[attr-defined]

    defaults = {
        "user": create_user(),
        "public_username": "test-user",
        "first_name": "Test",
        "last_name": "User",
        "title": "Developer",
        "subtitle": "Building things",
        "specialty": "Software",
        "short_description": "A test profile.",
    }
    defaults.update(overrides)
    return PublicProfile(**defaults)
