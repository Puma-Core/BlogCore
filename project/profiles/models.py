import re
from functools import cached_property
from typing import Any, Self

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


_PLACEHOLDER_PATTERN = re.compile(r"\{(\w+)\}")


def _extract_placeholders(template_url: str) -> list[str]:
    return _PLACEHOLDER_PATTERN.findall(template_url or "")


class Variable(models.Model):
    identifier = models.CharField(max_length=32, unique=True)
    label = models.CharField(max_length=16)
    description = models.CharField(max_length=64)
    regex = models.CharField(max_length=255)

    class Meta:
        ordering = ("identifier",)

    def __str__(self) -> str:
        return self.identifier

    @cached_property
    def _pattern(self) -> re.Pattern[str]:
        return re.compile(self.regex)

    def matches(self, value: str) -> bool:
        return self._pattern.fullmatch(value) is not None

    def clean(self) -> None:
        super().clean()
        try:
            re.compile(self.regex)
        except re.error as exc:
            raise ValidationError({"regex": f"Invalid regular expression: {exc}"})


class SocialNetworkConfig(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    template_url = models.CharField(max_length=255)
    icon_url = models.CharField(max_length=255)
    variables = models.ManyToManyField(
        Variable, related_name="configs"
    )
    archived = models.BooleanField(default=False)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        self._validate_template_url_variables()

    def _validate_template_url_variables(self) -> None:
        placeholders = set(self._template_placeholders())
        if not placeholders:
            return
        variable_identifiers = {
            variable.identifier for variable in self._associated_variables()
        }
        unknown = sorted(placeholders - variable_identifiers)
        if unknown:
            raise ValidationError(
                {
                    "template_url": (
                        "Template references variables not associated "
                        f"with the configuration: {unknown}."
                    )
                }
            )

    def _associated_variables(self) -> "models.QuerySet[Variable, Variable] | list[Variable]":
        return self.variables.all()

    def _template_placeholders(self) -> list[str]:
        return _extract_placeholders(self.template_url)


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


class VariableInstance(models.Model):
    social_network_instance = models.ForeignKey(
        SocialNetworkInstance,
        on_delete=models.PROTECT,
        related_name="variable_instances",
    )
    variable = models.ForeignKey(
        Variable, on_delete=models.PROTECT, related_name="instances"
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
            "Variable instances cannot be deleted.", protected_objects
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
            "variable_id", "social_network_instance_id"
        ).get(pk=self.pk)
        if current["variable_id"] != self.variable.pk:
            raise ValidationError(
                {"variable": "The variable of an instance cannot change."}
            )
        if current["social_network_instance_id"] != getattr(
            self, "social_network_instance_id"
        ):
            raise ValidationError(
                {
                    "social_network_instance": (
                        "The parent social network instance cannot change."
                    )
                }
            )

    def _ensure_value_matches_regex(self) -> None:
        if not self.variable_id:
            return
        if not self.variable.matches(self.value):
            raise ValidationError(
                {"value": "Value does not match the variable regex."}
            )


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
    def social_networks(self) -> models.QuerySet["SocialNetworkInstance"]:
        return SocialNetworkInstance.objects.filter(
            public_profile_links__public_profile=self,
            archived=False,
        )

    def __str__(self: "PublicProfile") -> str:
        return self.public_username


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
