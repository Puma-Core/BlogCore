import pytest
from django.contrib import admin

from posts.admin import PostAdmin
from posts.forms import PostForm
from posts.models import Post
from profiles.models import PublicProfile


@pytest.fixture
def post_admin() -> PostAdmin:
    return PostAdmin(Post, admin.site)


def test_post_is_registered_in_default_admin_site() -> None:
    assert Post in admin.site._registry
    assert isinstance(admin.site._registry[Post], PostAdmin)


def test_admin_lists_public_profile_author(post_admin) -> None:
    assert post_admin.list_display == ("title", "author", "created_at")


def test_admin_selects_author_for_changelist(post_admin) -> None:
    assert post_admin.list_select_related == ("author",)


def test_admin_uses_the_vditor_post_form(post_admin) -> None:
    assert post_admin.form is PostForm


def test_admin_form_uses_public_profiles_for_authors(post_admin) -> None:
    form = post_admin.get_form(request=None)

    assert form.base_fields["author"].queryset.model is PublicProfile
