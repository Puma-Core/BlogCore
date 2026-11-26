from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

from django.contrib.auth.models import AnonymousUser


def _request(
    *,
    is_staff: bool = True,
    has_perm: bool = True,
    is_authenticated: bool = True,
    is_active: bool = True,
    path: str = "/admin/",
    has_profile: bool = False,
    user_id: int = 1,
    username: str = "test-user",
    first_name: str = "Test",
    last_name: str = "User",
    user: Any | None = None,
) -> SimpleNamespace:
    """Return a lightweight request stand-in for unit tests.

    The default user is an authenticated staff member with the requested
    permissions. Pass ``is_authenticated=False`` to simulate an anonymous
    request, or provide a custom ``user`` object (for example an unsaved
    ``User`` instance) when the test needs a real model instance.
    """
    request = SimpleNamespace()
    request.path = path

    if user is not None:
        request.user = user
    elif not is_authenticated:
        request.user = SimpleNamespace(
            __class__=AnonymousUser,
            is_authenticated=False,
            is_staff=False,
            is_active=False,
        )
    else:
        request.user = SimpleNamespace(
            is_authenticated=True,
            is_staff=is_staff,
            is_active=is_active,
            id=user_id,
            pk=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            has_perm=MagicMock(return_value=has_perm),
        )
        if has_profile:
            request.user.public_profile = SimpleNamespace()

    return request
