import importlib

import pytest


migration = importlib.import_module("posts.migrations.0002_post_author_public_profile")


class _FilteredPosts:
    def __init__(self, updates: list[tuple[dict, dict]], filters: dict) -> None:
        self._updates = updates
        self._filters = filters

    def update(self, **values: int) -> None:
        self._updates.append((self._filters, values))


class _PostsManager:
    def __init__(self, author_ids: list[int], field_name: str) -> None:
        self._author_ids = author_ids
        self._field_name = field_name
        self.updates: list[tuple[dict, dict]] = []

    def values_list(self, field_name: str, *, flat: bool) -> list[int]:
        assert field_name == self._field_name
        assert flat is True
        return self._author_ids

    def filter(self, **filters: int) -> _FilteredPosts:
        return _FilteredPosts(self.updates, filters)


class _ProfilesManager:
    def __init__(self, identifiers: list[tuple[int, int]]) -> None:
        self._identifiers = identifiers

    def values_list(self, *field_names: str) -> list[tuple[int, int]]:
        assert field_names in (("user_id", "pk"), ("pk", "user_id"))
        return self._identifiers


class _Apps:
    def __init__(self, posts_manager: _PostsManager, profile_identifiers: list[tuple[int, int]]) -> None:
        self._post = type("Post", (), {"objects": posts_manager})
        self._profile = type(
            "PublicProfile",
            (), {"objects": _ProfilesManager(profile_identifiers)},
        )

    def get_model(self, app_label: str, model_name: str):
        if (app_label, model_name) == ("posts", "Post"):
            return self._post
        if (app_label, model_name) == ("profiles", "PublicProfile"):
            return self._profile
        raise LookupError((app_label, model_name))


def test_forward_migration_maps_each_post_author_to_its_public_profile() -> None:
    posts_manager = _PostsManager([1, 2], "user_author_id")
    apps = _Apps(posts_manager, [(1, 10), (2, 20)])

    migration.migrate_authors_to_profiles(apps, schema_editor=None)

    assert posts_manager.updates == [
        ({"user_author_id": 1}, {"profile_author_id": 10}),
        ({"user_author_id": 2}, {"profile_author_id": 20}),
    ]


def test_forward_migration_fails_before_updating_posts_without_profile() -> None:
    posts_manager = _PostsManager([1, 2], "user_author_id")
    apps = _Apps(posts_manager, [(1, 10)])

    with pytest.raises(RuntimeError, match=r"user IDs: \[2\]"):
        migration.migrate_authors_to_profiles(apps, schema_editor=None)

    assert posts_manager.updates == []


def test_reverse_migration_maps_each_public_profile_to_its_user() -> None:
    posts_manager = _PostsManager([10, 20], "profile_author_id")
    apps = _Apps(posts_manager, [(10, 1), (20, 2)])

    migration.migrate_authors_to_users(apps, schema_editor=None)

    assert posts_manager.updates == [
        ({"profile_author_id": 10}, {"user_author_id": 1}),
        ({"profile_author_id": 20}, {"user_author_id": 2}),
    ]


def test_reverse_migration_fails_before_updating_posts_without_user() -> None:
    posts_manager = _PostsManager([10, 20], "profile_author_id")
    apps = _Apps(posts_manager, [(10, 1)])

    with pytest.raises(RuntimeError, match=r"profile IDs: \[20\]"):
        migration.migrate_authors_to_users(apps, schema_editor=None)

    assert posts_manager.updates == []
