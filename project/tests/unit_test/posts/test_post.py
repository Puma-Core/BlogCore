import pytest
from django.core.exceptions import ValidationError

from posts.models import Post
from profiles.models import PublicProfile


def test_author_field_targets_public_profile() -> None:
    author = Post._meta.get_field("author")

    assert author.related_model is PublicProfile
    assert author.null is False
    assert author.remote_field.related_name == "posts"


def test_public_profile_exposes_posts_reverse_relation() -> None:
    posts_relation = PublicProfile._meta.get_field("posts")

    assert posts_relation.related_model is Post
    assert posts_relation.one_to_many is True


def test_post_keeps_assigned_public_profile_as_author() -> None:
    profile = PublicProfile(public_username="ada")
    post = Post(title="A post", content="Content", author=profile)

    assert post.author is profile


def test_post_string_representation_is_its_title() -> None:
    post = Post(title="A post", content="Content")

    assert str(post) == "A post"


@pytest.mark.django_db
def test_post_generates_a_url_safe_unique_name_from_title(
    public_profile_factory, user_factory
) -> None:
    author = public_profile_factory(
        user=user_factory(username="ada-user"),
        public_username="ada",
    )
    author.user.save()
    author.save()
    post = Post(
        title="  Hello, Django: A Guide!  ",
        content="Content",
        author=author,
    )

    post.save()

    assert post.unique_name == "hello-django-a-guide"


@pytest.mark.django_db
def test_post_recalculates_unique_name_when_title_changes(
    public_profile_factory, user_factory
) -> None:
    author = public_profile_factory(
        user=user_factory(username="ada-user"),
        public_username="ada",
    )
    author.user.save()
    author.save()
    post = Post(
        title="First title",
        content="Content",
        author=author,
    )
    post.save()

    post.title = "Updated title"
    post.save()

    assert post.unique_name == "updated-title"


@pytest.mark.django_db
def test_post_rejects_duplicate_unique_name_for_same_author(
    public_profile_factory, user_factory
) -> None:
    author = public_profile_factory(
        user=user_factory(username="ada-user"),
        public_username="ada",
    )
    author.user.save()
    author.save()
    Post(title="Hello world", content="First", author=author).save()
    duplicate = Post(title="Hello, world!", content="Second", author=author)

    with pytest.raises(ValidationError, match="Unique name"):
        duplicate.save()


@pytest.mark.django_db
def test_post_allows_same_unique_name_for_different_authors(
    public_profile_factory, user_factory
) -> None:
    first_author = public_profile_factory(
        user=user_factory(username="ada-user"),
        public_username="ada",
    )
    first_author.user.save()
    first_author.save()
    second_author = public_profile_factory(
        user=user_factory(username="grace-user"),
        public_username="grace",
    )
    second_author.user.save()
    second_author.save()
    first = Post(
        title="Hello world",
        content="First",
        author=first_author,
    )
    second = Post(
        title="Hello, world!",
        content="Second",
        author=second_author,
    )

    first.save()
    second.save()

    assert first.unique_name == second.unique_name == "hello-world"
