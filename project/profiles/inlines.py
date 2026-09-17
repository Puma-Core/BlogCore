from typing import cast

from django import forms
from django.contrib.admin import TabularInline
from profiles.models import (
    PublicProfileSocialNetwork,
    SocialNetworkInstance,
    VariableInstance,
)


def _missing_config_variables(instance):
    if instance is None or not instance.pk or not instance.config_id:
        return []

    existing_variable_ids = instance.variable_instances.values_list(
        "variable_id", flat=True
    )
    return instance.config.variables.exclude(pk__in=existing_variable_ids)


class VariableInstanceInlineFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        initial = list(kwargs.get("initial") or [])
        initial.extend(
            {"variable": variable.pk}
            for variable in _missing_config_variables(instance)
        )
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["social_network_instance"] = self.instance
        return kwargs


class VariableInstanceForm(forms.ModelForm):
    class Meta:
        model = VariableInstance
        fields = ("variable", "value")

    def __init__(self, *args, social_network_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        if (
            social_network_instance is not None
            and social_network_instance.config_id
        ):
            variable_field = cast(
                forms.ModelChoiceField,
                self.fields["variable"],
            )
            variable_field.queryset = (
                social_network_instance.config.variables.all()
            )
            widget = variable_field.widget
            widget.attrs["style"] = "pointer-events: none;"
            widget.attrs["tabindex"] = "-1"
            widget.can_add_related = False
            widget.can_change_related = False
            widget.can_delete_related = False
            widget.can_view_related = False

    def clean_variable(self):
        initial_variable = self.initial.get("variable")
        if initial_variable is None:
            return self.cleaned_data["variable"]
        initial_variable_id = getattr(initial_variable, "pk", initial_variable)
        variable_field = cast(
            forms.ModelChoiceField,
            self.fields["variable"],
        )
        if variable_field.queryset is None:
            return self.cleaned_data["variable"]
        return variable_field.queryset.get(pk=initial_variable_id)


class PublicProfileSocialNetworkInline(TabularInline):
    model = PublicProfileSocialNetwork
    extra = 0
    can_delete = False
    verbose_name_plural = "Public Profile"

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj is not None:
            getattr(formset.form, "base_fields")["social_network_instance"].queryset = SocialNetworkInstance.objects.filter(
                archived=False,
            )
        return formset


class VariableInstanceInline(TabularInline):
    model = VariableInstance
    verbose_name_plural = "Variable Instances"
    form = VariableInstanceForm
    formset = VariableInstanceInlineFormSet

    can_delete = False
    validate_max = True

    def get_extra(self, request, obj=None, **kwargs):
        return len(_missing_config_variables(obj))

    def get_max_num(self, request, obj=None, **kwargs):
        if obj is None or not obj.config_id:
            return 0
        return obj.config.variables.count()

    def has_delete_permission(self, request, obj=None):
        return False

    class Media:
        css = {"all": ("profiles/variable_instance_inline.css",)}
