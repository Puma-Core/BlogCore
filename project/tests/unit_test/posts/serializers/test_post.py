import pytest

from posts.models import Post
from posts.serializers import PostDetailSerializer, PostListSerializer


def test_post_list_serializer_exposes_only_summary_fields(
    public_profile_factory,
) -> None:
    author = public_profile_factory(first_name="Ada", last_name="Lovelace")
    post = Post(
        title="A post",
        content="Full content that must not be exposed by the list serializer.",
        unique_name="a-post",
        author=author,
    )
    post.content_preview = "Summary"

    serialized = PostListSerializer(post).data

    assert serialized == {
        "unique_name": "a-post",
        "title": "A post",
        "content_preview": "Summary",
        "created_at": None,
        "author_full_name": "Ada Lovelace",
    }


def test_post_detail_serializer_exposes_complete_content(
    public_profile_factory,
) -> None:
    author = public_profile_factory(first_name="Ada", last_name="Lovelace")
    post = Post(
        title="A post",
        content="Complete article content.",
        unique_name="a-post",
        author=author,
    )

    serialized = PostDetailSerializer(post).data

    assert serialized == {
        "unique_name": "a-post",
        "title": "A post",
        "content": "Complete article content.",
        "created_at": None,
        "updated_at": None,
        "public_username": "test-user",
        "author_full_name": "Ada Lovelace",
    }


@pytest.mark.django_db
def test_post_preview_queryset_limits_content_in_database(
    public_profile_factory,
    user_factory,
) -> None:
    author = public_profile_factory(
        user=user_factory(username="ada-user"),
        public_username="ada",
    )
    author.user.save()
    author.save()
    post = Post(title="A post", content="a" * 300, author=author)
    post.save()

    preview_post = Post.objects.with_content_preview().get(pk=post.pk)

    assert preview_post.content_preview == "a" * 256
    assert "content" in preview_post.get_deferred_fields()
