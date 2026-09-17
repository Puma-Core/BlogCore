from typing import Any

from django.core.exceptions import ValidationError
from django.db import models

from .public_profile import PublicProfile
from .social_network_instance import SocialNetworkInstance


class PublicProfileSocialNetwork(models.Model):
    public_profile = models.ForeignKey(
        PublicProfile,
        on_delete=models.CASCADE,
        related_name="social_network_links",
    )
    social_network_instance = models.ForeignKey(
        SocialNetworkInstance,
        on_delete=models.PROTECT,
        related_name="public_profile_links",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("public_profile", "social_network_instance"),
                name="unique_public_profile_social_network",
            )
        ]

    def clean(self) -> None:
        super().clean()
        if (
            getattr(self, "public_profile_id", None)
            and getattr(self, "social_network_instance_id", None)
        ):
            if self.public_profile.user_id != self.social_network_instance.author_id:
                raise ValidationError(
                    {
                        "social_network_instance": (
                            "The social network instance must belong to the "
                            "public profile user."
                        )
                    }
                )
            if self.social_network_instance.archived:
                raise ValidationError(
                    {
                        "social_network_instance": (
                            "Archived social network instances cannot be "
                            "added to a public profile."
                        )
                    }
                )

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)
