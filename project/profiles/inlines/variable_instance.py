from profiles.utils import missing_config_variables
from profiles.formsets.variable_instance import VariableInstanceInlineFormSet
from profiles.forms.variable_instance import VariableInstanceForm
from profiles.models import VariableInstance
from django.contrib.admin import TabularInline

class VariableInstanceInline(TabularInline):
    model = VariableInstance
    verbose_name_plural = "Variable Instances"
    form = VariableInstanceForm
    formset = VariableInstanceInlineFormSet

    can_delete = False
    validate_max = True

    def get_extra(self, request, obj=None, **kwargs):
        return len(missing_config_variables(obj))

    def get_max_num(self, request, obj=None, **kwargs):
        if obj is None or not obj.config_id:
            return 0
        return obj.config.variables.count()

    def has_delete_permission(self, request, obj=None):
        return False

    class Media:
        css = {"all": ("profiles/variable_instance_inline.css",)}
