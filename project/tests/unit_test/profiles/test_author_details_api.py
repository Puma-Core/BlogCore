import pytest
from django.urls import Resolver404, resolve
from rest_framework.test import APIRequestFactory

from profiles.models import PublicProfile
from profiles.serializers import PublicProfileSerializer
from profiles.views import PublicProfileViewSet

from tests.factories import create_public_profile


def test_public_profile_serializer_exposes_only_public_author_fields() -> None:
    profile = create_public_profile(photo_url="https://example.test/photo.jpg")

    serialized = PublicProfileSerializer(profile).data

    assert set(serialized) == {
        "public_username",
        "first_name",
        "last_name",
        "title",
        "subtitle",
        "specialty",
        "short_description",
        "photo_url",
        "fullname",
        "social_networks",
    }
    assert serialized["public_username"] == "test-user"
    assert serialized["photo_url"] == "https://example.test/photo.jpg"
    assert serialized["fullname"] == "Test User"
    assert serialized["social_networks"] == []


def test_public_profile_view_returns_author_details(mocker) -> None:
    profile = create_public_profile()
    queryset = mocker.Mock(model=PublicProfile)
    queryset.get.return_value = profile
    manager_all = mocker.patch.object(
        PublicProfile._default_manager,
        "all",
        return_value=queryset,
    )
    request = APIRequestFactory().get("/api/authors/test-user/")
    view = PublicProfileViewSet.as_view({"get": "retrieve"})
    mocker.patch.object(PublicProfileViewSet, "get_queryset", return_value=PublicProfile)

    response = view(request, public_username="test-user")

    manager_all.assert_called_once_with()
    queryset.get.assert_called_once_with(public_username="test-user")
    assert response.status_code == 200
    assert response.data["public_username"] == "test-user"
    assert response.data["first_name"] == "Test"


def test_public_profile_route_resolves_by_public_username() -> None:
    resolved = resolve("/api/authors/test-user/")

    assert resolved.url_name == "author-detail"


def test_anonymous_get_returns_public_author_details(mocker) -> None:
    profile = create_public_profile()
    queryset = mocker.Mock(model=PublicProfile)
    queryset.get.return_value = profile
    mocker.patch.object(PublicProfile._default_manager, "all", return_value=queryset)
    request = APIRequestFactory().get("/api/authors/test-user/")
    view = PublicProfileViewSet.as_view({"get": "retrieve"})
    mocker.patch.object(PublicProfileViewSet, "get_queryset", return_value=PublicProfile)

    response = view(request, public_username="test-user")

    queryset.get.assert_called_once_with(public_username="test-user")
    assert response.status_code == 200
    assert response.data["public_username"] == "test-user"


def test_missing_public_username_returns_not_found(mocker) -> None:
    queryset = mocker.Mock(model=PublicProfile)
    queryset.get.side_effect = PublicProfile.DoesNotExist
    manager_all = mocker.patch.object(
        PublicProfile._default_manager,
        "all",
        return_value=queryset,
    )
    request = APIRequestFactory().get("/api/authors/missing/")
    view = PublicProfileViewSet.as_view({"get": "retrieve"})
    mocker.patch.object(PublicProfileViewSet, "get_queryset", return_value=PublicProfile)

    response = view(request, public_username="missing")

    manager_all.assert_called_once_with()
    queryset.get.assert_called_once_with(public_username="missing")
    assert response.status_code == 404


def test_empty_public_username_does_not_match_route() -> None:
    with pytest.raises(Resolver404):
        resolve("/api/authors//")


def test_empty_photo_url_is_preserved() -> None:
    profile = create_public_profile(photo_url="")

    assert PublicProfileSerializer(profile).data["photo_url"] == ""


def test_author_endpoint_has_no_list_route() -> None:
    with pytest.raises(Resolver404):
        resolve("/api/authors/")


def test_author_endpoint_rejects_write_operations() -> None:
    request = APIRequestFactory().post("/api/authors/test-user/", {})
    view = PublicProfileViewSet.as_view({"get": "retrieve"})

    response = view(request, public_username="test-user")

    assert response.status_code == 403


def test_author_view_uses_public_username_lookup() -> None:
    assert PublicProfileViewSet.lookup_field == "public_username"
