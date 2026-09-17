from profiles.models import _extract_placeholders, SocialNetworkConfig
from typing import Any

from django import forms



class SocialNetworkConfigForm(forms.ModelForm):
    class Meta:
        model = SocialNetworkConfig
        fields = ("name", "template_url", "icon_url", "variables", "archived")

    def clean(self) -> dict:
        cleaned_data: dict[str, Any] = super().clean() or {}
        template_url = cleaned_data.get("template_url", "") or ""
        variables = cleaned_data.get("variables") or []
        placeholders = set(_extract_placeholders(template_url))
        if placeholders:
            variable_identifiers = {variable.identifier for variable in variables}
            unknown = sorted(placeholders - variable_identifiers)
            if unknown:
                raise forms.ValidationError(
                    {
                        "template_url": (
                            "Template references variables not associated "
                            f"with the configuration: {unknown}."
                        )
                    }
                )
        return cleaned_data
