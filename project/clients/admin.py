from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from clients.widgets.read_only_text.widget import ReadOnlyTextWidget

from .models import Client


class ClientAdminForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"
        widgets = {
            "secret": ReadOnlyTextWidget,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get("secret"):
            self.initial["secret"] = Client.generate_secret()


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientAdminForm
    list_display = ("name", "domain", "is_active", "created_at")
    list_filter = ("is_active", "groups")
    search_fields = ("name", "domain")
    ordering = ("-created_at",)
    filter_horizontal = ("groups", "permissions")
    readonly_fields = ("created_at", "updated_at")

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if "secret" in fields:
            fields.remove("secret")
        if not obj:
            fields.insert(2, "secret")
        return fields
