from profiles.forms.social_network_instance import SocialNetworkInstanceForm
from profiles.inlines import VariableInstanceInline
from django.contrib import admin

from profiles.models import SocialNetworkInstance

@admin.register(SocialNetworkInstance)
class SocialNetworkInstanceAdmin(admin.ModelAdmin):
    inlines = (VariableInstanceInline,)
    form = SocialNetworkInstanceForm
    def has_view_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
