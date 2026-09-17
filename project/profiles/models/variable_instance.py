from typing import Any

from django.core.exceptions import ValidationError
from django.db import models

from .social_network_instance import SocialNetworkInstance
from .variable import Variable


class VariableInstance(models.Model):
    social_network_instance = models.ForeignKey(
        SocialNetworkInstance,
        on_delete=models.PROTECT,
        related_name="variable_instances",
    )
    variable = models.ForeignKey(
        Variable,
        on_delete=models.PROTECT,
        related_name="instances",
    )
    value = models.CharField(max_length=255)
    archived = models.BooleanField(default=False)

    class Meta:
        ordering = ("variable__identifier",)

    def __str__(self) -> str:
        return f"{self.variable.identifier}={self.value}"

    @property
    def owner(self) -> Any:
        return self.social_network_instance.author

    def clean(self) -> None:
        super().clean()
        self._ensure_not_archived()
        self._ensure_identity_preserved()
        self._ensure_value_matches_regex()

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk is not None:
            self._ensure_not_archived()
            self._ensure_identity_preserved()
        super().save(*args, **kwargs)

    def archive(self) -> None:
        self.archived = True
        self.save(update_fields=["archived"])

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        protected_objects: set[models.Model] = set()
        if self.pk is not None:
            protected_objects.add(self)
        raise models.ProtectedError(
            "Variable instances cannot be deleted.",
            protected_objects,
        )

    def _ensure_not_archived(self) -> None:
        if not self.pk:
            return
        archived = (
            VariableInstance.objects.filter(pk=self.pk)
            .values_list("archived", flat=True)
            .first()
        )
        if archived:
            raise ValidationError(
                "Archived variable instances cannot be modified."
            )

    def _ensure_identity_preserved(self) -> None:
        if not self.pk:
            return
        current = VariableInstance.objects.values(
            "variable_id",
            "social_network_instance_id",
        ).get(pk=self.pk)
        if current["variable_id"] != self.variable.pk:
            raise ValidationError(
                {"variable": "The variable of an instance cannot change."}
            )
        if current["social_network_instance_id"] != getattr(
            self,
            "social_network_instance_id",
        ):
            raise ValidationError(
                {
                    "social_network_instance": (
                        "The parent social network instance cannot change."
                    )
                }
            )

    def _ensure_value_matches_regex(self) -> None:
        if not getattr(self, "variable_id"):
            return
        if not self.variable.matches(self.value):
            raise ValidationError(
                {"value": "Value does not match the variable regex."}
            )
