from profiles.inlines import PublicProfileSocialNetworkInline
from django import forms
from django.contrib import admin
from django.http import HttpRequest

from profiles.models import PublicProfile


class PublicProfileForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is not None and not self.instance.pk:
            self.fields["public_username"].initial = user.username
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name

    class Meta:
        model = PublicProfile
        fields = (
            "public_username",
            "first_name",
            "last_name",
            "title",
            "subtitle",
            "specialty",
            "short_description",
            "photo_url",
        )


@admin.register(PublicProfile)
class PublicProfileAdmin(admin.ModelAdmin):
    form = PublicProfileForm
    add_form_template = "admin/profiles/publicprofile/change_form.html"
    change_form_template = "admin/profiles/publicprofile/change_form.html"
    inlines = [PublicProfileSocialNetworkInline,]

    def get_form(
        self,
        request: HttpRequest,
        obj: PublicProfile | None = None,
        change: bool = False,
        **kwargs,
    ):
        form_class = super().get_form(request, obj, change, **kwargs)

        def __init__(inner_self, *args, **inner_kwargs):
            inner_kwargs["user"] = getattr(request, "user")
            form_class.__init__(inner_self, *args, **inner_kwargs)

        return type("BoundPublicProfileForm", (form_class,), {"__init__": __init__})

    def get_queryset(self, request: HttpRequest):
        if request is None or not getattr(request, "user").is_authenticated:
            return super().get_queryset(request).none()
        return super().get_queryset(request).filter(user_id=getattr(getattr(request, "user"), "id"))

    def has_module_permission(self, request: HttpRequest) -> bool:
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.is_staff)

    def has_add_permission(self, request: HttpRequest) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated or not user.is_staff:
            return False
        return not PublicProfile.objects.filter(user_id=user.id).exists()

    def has_change_permission(
        self, request: HttpRequest, obj: PublicProfile | None = None
    ) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated or not user.is_staff:
            return False
        if obj is None:
            return PublicProfile.objects.filter(user_id=user.id).exists()
        return getattr(obj, "user_id") == user.id

    def has_view_permission(
        self, request: HttpRequest, obj: PublicProfile | None = None
    ) -> bool:
        return self.has_change_permission(request, obj)

    def has_delete_permission(
        self, request: HttpRequest, obj: PublicProfile | None = None
    ) -> bool:
        return False

    def save_model(
        self,
        request: HttpRequest,
        obj: PublicProfile,
        form: forms.ModelForm,
        change: bool,
    ) -> None:
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)
