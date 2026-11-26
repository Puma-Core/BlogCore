from urllib.parse import urlparse

from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import validate_domains


class Client(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("name"),
    )
    domain = models.TextField(
        verbose_name=_("allowed domains"),
        help_text=_("Comma-separated list of allowed URLs including protocol (e.g. https://example.com,http://app.example.org)."),
        validators=[validate_domains],
    )
    secret = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name=_("secret token"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("active"),
    )
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="clients",
        verbose_name=_("groups"),
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="clients",
        verbose_name=_("permissions"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("updated at"),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("client")
        verbose_name_plural = _("clients")

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = self.generate_secret()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_secret() -> str:
        import secrets
        return secrets.token_urlsafe(32)

    def has_perm(self, codename: str) -> bool:
        if self.permissions.filter(codename=codename).exists():
            return True
        return self.groups.filter(permissions__codename=codename).exists()

    def has_module_perms(self, app_label: str) -> bool:
        if self.permissions.filter(content_type__app_label=app_label).exists():
            return True
        return self.groups.filter(
            permissions__content_type__app_label=app_label
        ).exists()

    def is_domain_allowed(self, host: str) -> bool:
        allowed_hosts = {self._extract_hostname(url) for url in self.domain.split(",")}
        return host in allowed_hosts

    @staticmethod
    def _extract_hostname(url: str) -> str:
        parsed = urlparse(url.strip())
        return parsed.hostname or ""
