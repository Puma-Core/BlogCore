from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .social_network_instance import SocialNetworkInstance


class PublicProfile(models.Model):
    objects = models.Manager()

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="public_profile",
    )
    public_username = models.CharField(max_length=64, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=150)
    specialty = models.CharField(max_length=150)
    short_description = models.TextField()
    photo_url = models.URLField(max_length=255, blank=True)

    class Meta:
        ordering = ("public_username",)

    def clean(self) -> None:
        super().clean()
        self._ensure_user_preserved()

    def save(self, *args: Any, **kwargs: Any) -> None:
        self._ensure_user_preserved()
        super().save(*args, **kwargs)

    def _ensure_user_preserved(self) -> None:
        if not self.pk:
            return
        current_user_id = (
            PublicProfile.objects.filter(pk=self.pk)
            .values_list("user_id", flat=True)
            .first()
        )
        if current_user_id is not None and current_user_id != getattr(self, "user_id"):
            raise ValidationError(
                {"user": "The user of a public profile cannot change."}
            )

    @property
    def social_networks(self) -> models.QuerySet[SocialNetworkInstance]:
        return SocialNetworkInstance.objects.filter(
            public_profile_links__public_profile=self,
            archived=False,
        )

    def __str__(self) -> str:
        return self.public_username
