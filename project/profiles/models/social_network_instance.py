from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .social_network_config import SocialNetworkConfig, _extract_placeholders

if TYPE_CHECKING:
    from .variable_instance import VariableInstance


class SocialNetworkInstance(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="social_network_instances",
    )
    config = models.ForeignKey(
        SocialNetworkConfig,
        on_delete=models.PROTECT,
        related_name="instances",
    )
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.config.name} ({self.author})"

    @property
    def icon_url(self) -> str:
        return self.config.icon_url

    @property
    def url(self) -> str | None:
        placeholders = _extract_placeholders(self.config.template_url)
        if not placeholders:
            return self.config.template_url
        active_values = {
            instance.variable.identifier: instance.value
            for instance in self._active_variable_instances()
            if instance.value
        }
        if any(placeholder not in active_values for placeholder in placeholders):
            return None
        return self.config.template_url.format_map(active_values)

    def clean(self) -> None:
        super().clean()
        self._ensure_variable_instances_match_config()

    def _active_variable_instances(self) -> models.QuerySet["VariableInstance"]:
        return getattr(self, "variable_instances").filter(archived=False)

    def _iter_variable_instances(self) -> models.QuerySet["VariableInstance"]:
        return getattr(self, "variable_instances").all()

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk is not None:
            state = self._load_state()
            self._ensure_not_archived(state)
            self._ensure_author_preserved(state)
        super().save(*args, **kwargs)

    def archive(self) -> None:
        self.archived = True
        self.save(update_fields=["archived"])

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        if self.archived:
            protected_objects: set[models.Model] = set()
            if self.pk is not None:
                protected_objects.add(self)
            raise models.ProtectedError(
                "Archived social network instances cannot be deleted.",
                protected_objects,
            )
        return super().delete(*args, **kwargs)

    def _ensure_variable_instances_match_config(self) -> None:
        if not self.pk or not getattr(self, "config_id"):
            return
        config_variable_identifiers = {
            variable.identifier for variable in self.config._associated_variables()
        }
        for variable_instance in self._iter_variable_instances():
            if (
                variable_instance.variable.identifier
                not in config_variable_identifiers
            ):
                raise ValidationError(
                    {
                        "variable_instances": (
                            f"Variable {variable_instance.variable.identifier} "
                            "is not defined for the configuration of this "
                            "social network instance."
                        )
                    }
                )

    def _load_state(self) -> dict[str, Any] | None:
        if not self.pk:
            return None
        return (
            SocialNetworkInstance.objects.filter(pk=self.pk)
            .values("archived", "author_id")
            .first()
        )

    def _ensure_not_archived(self, state: dict[str, Any] | None) -> None:
        if not state:
            return
        if state.get("archived"):
            raise ValidationError(
                "Archived social network instances cannot be modified."
            )

    def _ensure_author_preserved(self, state: dict[str, Any] | None) -> None:
        if not state:
            return
        if state.get("author_id") != getattr(self, "author_id"):
            raise ValidationError(
                {
                    "author": (
                        "The author of a social network instance cannot change."
                    )
                }
            )
