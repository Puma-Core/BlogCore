from django.shortcuts import redirect
from django.urls import resolve, Resolver404


class PublicProfileOnboardingMiddleware:
    """Redirect staff users without a PublicProfile to the profile creation form.

    The middleware only inspects requests under the Django admin URL prefix.
    Active staff users who do not have a public profile are redirected to the
    standard admin add view for ``PublicProfile``. Login, logout, password
    change and the profile add view itself are exempt so the user can complete
    the flow without being redirected in a loop.
    """

    ADMIN_PREFIX = "/admin/"

    EXEMPT_ADMIN_URL_NAMES = {
        "admin:login",
        "admin:logout",
        "admin:password_change",
        "admin:password_change_done",
        "admin:profiles_publicprofile_add",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._must_onboard(request):
            return redirect("admin:profiles_publicprofile_add")
        return self.get_response(request)

    def _must_onboard(self, request) -> bool:
        if not request.path.startswith(self.ADMIN_PREFIX):
            return False

        user = request.user
        if not user.is_authenticated or not user.is_staff:
            return False

        if self._is_exempt(request):
            return False

        return not hasattr(user, "public_profile")

    def _is_exempt(self, request) -> bool:
        try:
            match = resolve(request.path)
        except Resolver404:
            return False
        return match.view_name in self.EXEMPT_ADMIN_URL_NAMES
