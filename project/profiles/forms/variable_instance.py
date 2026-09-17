from typing import cast
from profiles.models import VariableInstance
from django import forms


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
        queryset = variable_field.queryset
        if queryset is None or not queryset.exists():
            return self.cleaned_data["variable"]
        return queryset.get(pk=initial_variable_id)
