import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from profiles.inlines import VariableInstanceForm
from profiles.inlines import (
    PublicProfileSocialNetworkInline,
    VariableInstanceInline,
    _missing_config_variables,
)
from profiles.models import (
    PublicProfile,
    SocialNetworkConfig,
    SocialNetworkInstance,
    Variable,
    VariableInstance,
)


@pytest.mark.django_db
def test_variable_instance_inline_prefills_missing_config_variables() -> None:
    user = get_user_model().objects.create_user(username="octocat")
    username = Variable.objects.create(
        identifier="username",
        label="Username",
        description="Social network username",
        regex=r"[A-Za-z0-9_]+",
    )
    company = Variable.objects.create(
        identifier="company",
        label="Company",
        description="Company name",
        regex=r"[A-Za-z0-9_]+",
    )
    config = SocialNetworkConfig.objects.create(
        name="LinkedIn",
        template_url="https://linkedin.com/in/{username}",
        icon_url="https://example.test/linkedin.svg",
    )
    config.variables.add(username, company)
    network = SocialNetworkInstance.objects.create(author=user, config=config)
    request = RequestFactory().get("/")
    request.user = user
    inline = VariableInstanceInline(SocialNetworkInstance, admin.site)
    formset_class = inline.get_formset(request, network)
    formset = formset_class(instance=network)

    assert [form.initial["variable"] for form in formset.forms] == [
        company.pk,
        username.pk,
    ]
    assert list(formset.forms[0].fields["variable"].queryset) == [
        company,
        username,
    ]
    assert formset.forms[0].fields["variable"].widget.attrs["tabindex"] == "-1"
    assert "archived" not in formset.forms[0].fields
    assert inline.get_max_num(request, network) == 2
    assert inline.has_delete_permission(request, network) is False


@pytest.mark.django_db
def test_variable_instance_inline_preserves_disabled_variables_on_post() -> None:
    user = get_user_model().objects.create_user(username="octocat")
    variable = Variable.objects.create(
        identifier="username",
        label="Username",
        description="Social network username",
        regex=r"[A-Za-z0-9_]+",
    )
    config = SocialNetworkConfig.objects.create(
        name="GitHub",
        template_url="https://github.com/{username}",
        icon_url="https://example.test/github.svg",
    )
    config.variables.add(variable)
    network = SocialNetworkInstance.objects.create(author=user, config=config)
    request = RequestFactory().post("/")
    request.user = user
    inline = VariableInstanceInline(SocialNetworkInstance, admin.site)
    formset_class = inline.get_formset(request, network)
    formset = formset_class(
        data={
            "variable_instances-TOTAL_FORMS": "1",
            "variable_instances-INITIAL_FORMS": "0",
            "variable_instances-MIN_NUM_FORMS": "0",
            "variable_instances-MAX_NUM_FORMS": "1",
            "variable_instances-0-variable": str(variable.pk),
            "variable_instances-0-value": "octocat",
        },
        instance=network,
    )

    assert formset.forms[0].initial["variable"] == variable.pk
    assert formset.forms[0].prefix == "variable_instances-0"
    assert formset.is_valid()

    form = VariableInstanceForm(
        data={"variable": str(variable.pk), "value": "octocat"},
        initial={"variable": variable.pk},
        instance=VariableInstance(social_network_instance=network),
        social_network_instance=network,
    )

    assert form.is_valid()
    assert form.cleaned_data["variable"] == variable

    form_without_initial = VariableInstanceForm(
        data={"variable": str(variable.pk), "value": "octocat"},
        instance=VariableInstance(social_network_instance=network),
        social_network_instance=network,
    )

    assert form_without_initial.is_valid()
    assert form_without_initial.cleaned_data["variable"] == variable


def test_variable_instance_inline_has_no_rows_without_a_network_instance() -> None:
    request = RequestFactory().get("/")
    inline = VariableInstanceInline(SocialNetworkInstance, admin.site)

    assert _missing_config_variables(None) == []
    assert inline.get_extra(request) == 0
    assert inline.get_max_num(request) == 0


@pytest.mark.django_db
def test_public_profile_inline_only_offers_active_social_networks() -> None:
    user = get_user_model().objects.create_user(username="octocat")
    profile = PublicProfile.objects.create(
        user=user,
        public_username="octocat",
        first_name="Octo",
        last_name="Cat",
        title="Engineer",
        subtitle="Building cool things",
        specialty="Backend",
        short_description="Hello world",
    )
    config = SocialNetworkConfig.objects.create(
        name="GitHub",
        template_url="https://github.com/octocat",
        icon_url="https://example.test/github.svg",
    )
    active = SocialNetworkInstance.objects.create(author=user, config=config)
    archived = SocialNetworkInstance.objects.create(
        author=user,
        config=config,
        archived=True,
    )
    request = RequestFactory().get("/")
    request.user = user
    inline = PublicProfileSocialNetworkInline(PublicProfile, admin.site)
    formset_class = inline.get_formset(request, profile)

    assert list(
        formset_class.form.base_fields["social_network_instance"].queryset
    ) == [active]
    assert archived not in formset_class.form.base_fields[
        "social_network_instance"
    ].queryset
