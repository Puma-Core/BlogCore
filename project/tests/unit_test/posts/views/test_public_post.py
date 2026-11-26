import pytest
from django.urls import Resolver404, resolve
from rest_framework.test import APIRequestFactory

from posts.models import Post
from posts.views import PublicProfilePostViewSet


list_view = PublicProfilePostViewSet.as_view({"get": "list"})
detail_view = PublicProfilePostViewSet.as_view({"get": "retrieve"})


def create_persisted_profile(public_profile_factory, user_factory, **overrides):
    user = user_factory(username=overrides.pop("user_username"))
    profile = public_profile_factory(user=user, **overrides)
    user.save()
    profile.save()
    return profile


@pytest.mark.django_db
def test_anonymous_get_lists_only_the_requested_author_posts(
    public_profile_factory, user_factory
) -> None:
    author = create_persisted_profile(
        public_profile_factory,
        user_factory,
        user_username="ada-user",
        public_username="ada",
        first_name="Ada",
        last_name="Lovelace",
    )
    other_author = create_persisted_profile(
        public_profile_factory,
        user_factory,
        user_username="grace-user",
        public_username="grace",
    )
    post = Post(title="Analytical Engine", content="a" * 300, author=author)
    post.save()
    Post(title="Compiler", content="Private to Grace", author=other_author).save()

    response = list_view(
        APIRequestFactory().get("/api/authors/ada/posts/"), public_username="ada"
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"] == [
        {
            "unique_name": "analytical-engine",
            "title": "Analytical Engine",
            "content_preview": "a" * 256,
            "created_at": post.created_at.isoformat().replace("+00:00", "Z"),
            "author_full_name": "Ada Lovelace",
        }
    ]


@pytest.mark.django_db
def test_anonymous_get_returns_a_post_scoped_to_its_author(
    public_profile_factory, user_factory
) -> None:
    author = create_persisted_profile(
        public_profile_factory,
        user_factory,
        user_username="ada-user",
        public_username="ada",
        first_name="Ada",
        last_name="Lovelace",
    )
    post = Post(title="Analytical Engine", content="Complete article", author=author)
    post.save()

    response = detail_view(
        APIRequestFactory().get("/api/authors/ada/posts/analytical-engine/"),
        public_username="ada",
        unique_name="analytical-engine",
    )

    assert response.status_code == 200
    assert response.data == {
        "unique_name": "analytical-engine",
        "title": "Analytical Engine",
        "content": "Complete article",
        "created_at": post.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": post.updated_at.isoformat().replace("+00:00", "Z"),
        "public_username": "ada",
        "author_full_name": "Ada Lovelace",
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("view", "path", "kwargs"),
    [
        (
            list_view,
            "/api/authors/missing/posts/",
            {"public_username": "missing"},
        ),
        (
            detail_view,
            "/api/authors/ada/posts/missing/",
            {"public_username": "ada", "unique_name": "missing"},
        ),
    ],
)
def test_missing_profile_or_post_returns_not_found(
    view, path, kwargs, public_profile_factory, user_factory
) -> None:
    create_persisted_profile(
        public_profile_factory,
        user_factory,
        user_username="ada-user",
        public_username="ada",
    )

    response = view(APIRequestFactory().get(path), **kwargs)

    assert response.status_code == 404


@pytest.mark.django_db
def test_post_slug_under_a_different_author_returns_not_found(
    public_profile_factory, user_factory
) -> None:
    author = create_persisted_profile(
        public_profile_factory,
        user_factory,
        user_username="ada-user",
        public_username="ada",
    )
    other_author = create_persisted_profile(
        public_profile_factory,
        user_factory,
        user_username="grace-user",
        public_username="grace",
    )
    Post(title="Analytical Engine", content="Grace's post", author=other_author).save()

    response = detail_view(
        APIRequestFactory().get("/api/authors/ada/posts/analytical-engine/"),
        public_username=author.public_username,
        unique_name="analytical-engine",
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("view", "path", "kwargs"),
    [
        (list_view, "/api/authors/ada/posts/", {"public_username": "ada"}),
        (
            detail_view,
            "/api/authors/ada/posts/analytical-engine/",
            {"public_username": "ada", "unique_name": "analytical-engine"},
        ),
    ],
)
def test_public_post_endpoints_reject_writes_without_mutating_data(
    view, path, kwargs, public_profile_factory, user_factory
) -> None:
    author = create_persisted_profile(
        public_profile_factory,
        user_factory,
        user_username="ada-user",
        public_username="ada",
    )
    Post(title="Analytical Engine", content="Original", author=author).save()
    post_count = Post.objects.count()

    response = view(APIRequestFactory().post(path, {"title": "New"}), **kwargs)

    assert response.status_code == 405
    assert Post.objects.count() == post_count


def test_public_profile_post_routes_resolve_with_trailing_slashes() -> None:
    list_route = resolve("/api/authors/ada/posts/")
    detail_route = resolve("/api/authors/ada/posts/analytical-engine/")

    assert list_route.func.cls is PublicProfilePostViewSet
    assert list_route.kwargs == {"public_username": "ada"}
    assert detail_route.func.cls is PublicProfilePostViewSet
    assert detail_route.kwargs == {
        "public_username": "ada",
        "unique_name": "analytical-engine",
    }


@pytest.mark.parametrize(
    "path",
    [
        "/api/authors/ada/posts",
        "/api/authors/ada/posts/analytical-engine",
    ],
)
def test_public_profile_post_routes_require_trailing_slashes(path: str) -> None:
    with pytest.raises(Resolver404):
        resolve(path)
