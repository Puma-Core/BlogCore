from django.contrib import admin
from django.test import RequestFactory

from profiles.admin.social_netowk_instance import SocialNetworkInstanceAdmin
from profiles.admin.variable_instance import VariableInstanceAdmin
from profiles.models import SocialNetworkInstance, VariableInstance


def test_social_network_instance_admin_disallows_view_and_delete() -> None:
    model_admin = SocialNetworkInstanceAdmin(SocialNetworkInstance, admin.site)
    request = RequestFactory().get("/")

    assert model_admin.has_view_permission(request) is False
    assert model_admin.has_delete_permission(request) is False


def test_variable_instance_admin_disallows_view_and_delete() -> None:
    model_admin = VariableInstanceAdmin(VariableInstance, admin.site)
    request = RequestFactory().get("/")

    assert model_admin.has_view_permission(request) is False
    assert model_admin.has_delete_permission(request) is False
