from profiles.admin.variable_instance import VariableInstanceAdmin
from profiles.admin.social_netowk_instance import SocialNetworkInstanceAdmin
from profiles.admin.public_profile import PublicProfileAdmin
from typing import Any
from django import forms
from django.contrib import admin

from profiles.models import SocialNetworkConfig, Variable, _extract_placeholders

__all__ = (
    PublicProfileAdmin,
    SocialNetworkInstanceAdmin,
    VariableInstanceAdmin
)

@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ("identifier", "label", "description")
    search_fields = ("identifier", "label", "description")
    ordering = ("identifier",)


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


@admin.register(SocialNetworkConfig)
class SocialNetworkConfigAdmin(admin.ModelAdmin):
    form = SocialNetworkConfigForm
    list_display = ("name", "template_url", "icon_url", )
    search_fields = ("name",)
    ordering = ("name",)
    filter_horizontal = ("variables",)
