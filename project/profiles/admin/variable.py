from profiles.models import Variable
from django.contrib import admin


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ("identifier", "label", "description")
    search_fields = ("identifier", "label", "description")
    ordering = ("identifier",)
