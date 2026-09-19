import pytest
from django.contrib.auth import get_user_model

from profiles.models import (
    PublicProfile,
    PublicProfileSocialNetwork,
    SocialNetworkConfig,
    SocialNetworkInstance,
)
from profiles.serializers import PublicProfileSerializer
from tests.factories import create_public_profile


def test_public_profile_serializer_fullname() -> None:
    profile = create_public_profile(first_name="Octo", last_name="Cat")

    serialized = PublicProfileSerializer(profile).data

    assert serialized["fullname"] == "Octo Cat"


@pytest.mark.django_db
def test_public_profile_serializer_exposes_active_social_networks() -> None:
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
    network = SocialNetworkInstance.objects.create(author=user, config=config)
    PublicProfileSocialNetwork.objects.create(
        public_profile=profile,
        social_network_instance=network,
    )

    serialized = PublicProfileSerializer(profile).data

    assert serialized["social_networks"] == [
        {
            "name": "GitHub",
            "url": "https://github.com/octocat",
            "icon_url": "https://example.test/github.svg",
        }
    ]
