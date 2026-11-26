from django import forms
from profiles.models import SocialNetworkInstance

class SocialNetworkInstanceForm(forms.ModelForm):
    class Meta:
        model = SocialNetworkInstance
        fields = ("__all__")
