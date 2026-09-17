from profiles.models import PublicProfileSocialNetwork, SocialNetworkInstance
from django.contrib.admin import TabularInline

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
