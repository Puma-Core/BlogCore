import re

from django.core.exceptions import ValidationError
from django.db import models

from .variable import Variable


_PLACEHOLDER_PATTERN = re.compile(r"\{(\w+)\}")


def _extract_placeholders(template_url: str) -> list[str]:
    return _PLACEHOLDER_PATTERN.findall(template_url or "")


class SocialNetworkConfig(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    template_url = models.CharField(max_length=255)
    icon_url = models.CharField(max_length=255)
    variables = models.ManyToManyField(Variable, related_name="configs")
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
