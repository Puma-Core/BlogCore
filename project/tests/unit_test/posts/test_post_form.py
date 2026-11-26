import pytest

from posts.forms import PostForm
from posts.models import Post
from posts.widgets import VditorWidget


def test_post_form_uses_vditor_for_content() -> None:
    form = PostForm()

    assert isinstance(form.fields["content"].widget, VditorWidget)


def test_post_form_loads_existing_markdown_unchanged(public_profile_factory) -> None:
    markdown = "# Heading\n\nExisting *Markdown*."
    form = PostForm(
        instance=Post(title="A post", content=markdown, author=public_profile_factory())
    )

    assert form["content"].value() == markdown


@pytest.mark.django_db
def test_post_form_persists_markdown_and_attachment_references(
    public_profile_factory, user_factory
) -> None:
    author = public_profile_factory(user=user_factory(username="ada-user"))
    author.user.save()
    author.save()
    markdown = "# Heading\n\n*Emphasis* and [link](https://example.com).\n\n![Photo](/media/attachments/photo.webp)"
    form = PostForm(
        data={"title": "Markdown post", "content": markdown, "author": author.pk}
    )

    assert form.is_valid(), form.errors
    post = form.save()
    assert post.content == markdown
