import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from profiles.models import (
    PublicProfile,
    PublicProfileSocialNetwork,
    SocialNetworkConfig,
    SocialNetworkInstance,
)

from tests.factories import create_public_profile


def test_profile_stores_constructor_attributes() -> None:
    profile = create_public_profile(
        public_username="octocat",
        first_name="Octo",
        last_name="Cat",
        title="Engineer",
        subtitle="Building cool things",
        specialty="Backend",
        short_description="Hello world",
        photo_url="https://example.test/avatar.png",
    )

    assert profile.public_username == "octocat"
    assert profile.first_name == "Octo"
    assert profile.last_name == "Cat"
    assert profile.title == "Engineer"
    assert profile.subtitle == "Building cool things"
    assert profile.specialty == "Backend"
    assert profile.short_description == "Hello world"
    assert profile.photo_url == "https://example.test/avatar.png"


def test_profile_str_returns_public_username() -> None:
    profile = create_public_profile(public_username="octocat")

    assert str(profile) == "octocat"


def test_profile_photo_url_can_be_blank() -> None:
    profile = create_public_profile(photo_url="")

    assert profile.photo_url == ""


def test_profile_public_username_field_is_unique() -> None:
    field = PublicProfile._meta.get_field("public_username")

    assert field.unique is True


def test_profile_photo_url_field_allows_blank() -> None:
    field = PublicProfile._meta.get_field("photo_url")

    assert field.blank is True


def test_profile_public_username_is_required() -> None:
    profile = create_public_profile()
    profile.public_username = ""

    with pytest.raises(ValidationError) as exc_info:
        profile.full_clean(exclude={"user"})

    assert "public_username" in exc_info.value.message_dict


@pytest.mark.django_db
def test_profile_accepts_valid_photo_url() -> None:
    profile = create_public_profile(photo_url="https://example.test/avatar.png")

    profile.full_clean(exclude={"user"})

    assert profile.photo_url == "https://example.test/avatar.png"


@pytest.mark.django_db
def test_profile_accepts_blank_photo_url() -> None:
    profile = create_public_profile(photo_url="")

    profile.full_clean(exclude={"user"})


@pytest.mark.django_db
def test_profile_rejects_invalid_photo_url() -> None:
    profile = create_public_profile(photo_url="not-a-url")

    with pytest.raises(ValidationError) as exc_info:
        profile.full_clean(exclude={"user"})

    assert "photo_url" in exc_info.value.message_dict


def _saved_profile_and_social_network() -> tuple[
    PublicProfile, SocialNetworkInstance
]:
    user = get_user_model().objects.create_user(username="octocat")
    profile = PublicProfile.objects.create(
        user=user,
        public_username="octocat",
        first_name="Octo",
        last_name="Cat",
        title="Engineer",
        subtitle="Building cool things",
        specialty="Backend",
        short_description="Hello world",
    )
    config = SocialNetworkConfig.objects.create(
        name="GitHub",
        template_url="https://github.com/octocat",
        icon_url="https://example.test/github.svg",
    )
    instance = SocialNetworkInstance.objects.create(author=user, config=config)
    return profile, instance


@pytest.mark.django_db
def test_profile_exposes_selected_active_social_networks() -> None:
    profile, instance = _saved_profile_and_social_network()
    PublicProfileSocialNetwork.objects.create(
        public_profile=profile,
        social_network_instance=instance,
    )

    assert list(profile.social_networks) == [instance]
    assert profile.social_networks[0].url == "https://github.com/octocat"
    assert profile.social_networks[0].icon_url == "https://example.test/github.svg"


@pytest.mark.django_db
def test_profile_excludes_archived_selected_social_networks() -> None:
    profile, instance = _saved_profile_and_social_network()
    PublicProfileSocialNetwork.objects.create(
        public_profile=profile,
        social_network_instance=instance,
    )
    instance.archived = True
    instance.save(update_fields=["archived"])

    assert list(profile.social_networks) == []


@pytest.mark.django_db
def test_profile_rejects_social_network_from_another_user() -> None:
    profile, _ = _saved_profile_and_social_network()
    other_user = get_user_model().objects.create_user(username="other-user")
    config = SocialNetworkConfig.objects.create(
        name="LinkedIn",
        template_url="https://linkedin.com/in/other-user",
        icon_url="https://example.test/linkedin.svg",
    )
    instance = SocialNetworkInstance.objects.create(author=other_user, config=config)

    with pytest.raises(ValidationError) as exc_info:
        PublicProfileSocialNetwork.objects.create(
            public_profile=profile,
            social_network_instance=instance,
        )

    assert "social_network_instance" in exc_info.value.message_dict


@pytest.mark.django_db
def test_profile_rejects_archived_social_network() -> None:
    profile, instance = _saved_profile_and_social_network()
    instance.archived = True
    instance.save(update_fields=["archived"])

    with pytest.raises(ValidationError) as exc_info:
        PublicProfileSocialNetwork.objects.create(
            public_profile=profile,
            social_network_instance=instance,
        )

    assert "social_network_instance" in exc_info.value.message_dict


@pytest.mark.django_db
def test_profile_rejects_duplicate_social_network_link() -> None:
    profile, instance = _saved_profile_and_social_network()
    PublicProfileSocialNetwork.objects.create(
        public_profile=profile,
        social_network_instance=instance,
    )

    duplicate = PublicProfileSocialNetwork(
        public_profile=profile,
        social_network_instance=instance,
    )

    with pytest.raises(ValidationError) as exc_info:
        duplicate.full_clean()

    assert "__all__" in exc_info.value.message_dict
