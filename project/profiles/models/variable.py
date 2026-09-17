import re
from functools import cached_property

from django.core.exceptions import ValidationError
from django.db import models


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
