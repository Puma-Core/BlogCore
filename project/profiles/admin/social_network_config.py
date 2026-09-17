from profiles.forms.social_network_config import SocialNetworkConfigForm
from profiles.models import SocialNetworkConfig
from django.contrib import admin


@admin.register(SocialNetworkConfig)
class SocialNetworkConfigAdmin(admin.ModelAdmin):
    form = SocialNetworkConfigForm
    list_display = ("name", "template_url", "icon_url", )
    search_fields = ("name",)
    ordering = ("name",)
    filter_horizontal = ("variables",)
