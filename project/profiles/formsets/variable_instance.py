from profiles.utils import missing_config_variables
from django import forms


class VariableInstanceInlineFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        initial = list(kwargs.get("initial") or [])
        initial.extend(
            {"variable": variable.pk}
            for variable in missing_config_variables(instance)
        )
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["social_network_instance"] = self.instance
        return kwargs
