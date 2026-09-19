from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _


def validate_domains(value: str) -> None:
    if not value:
        raise ValidationError(_("At least one allowed domain is required."))

    url_validator = URLValidator()
    domains = [entry.strip() for entry in value.split(",")]

    for domain in domains:
        if not domain:
            raise ValidationError(_("Empty domain entries are not allowed."))

        try:
            url_validator(domain)
        except ValidationError as exc:
            raise ValidationError(
                _("%(domain)s is not a valid URL with protocol."),
                params={"domain": domain},
            ) from exc
