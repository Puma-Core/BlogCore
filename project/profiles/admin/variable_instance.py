from profiles.models import VariableInstance
from django.contrib import admin

@admin.register(VariableInstance)
class VariableInstanceAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False