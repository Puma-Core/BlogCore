from django.conf import settings
from django.urls import include, path
from posts.views import PublicProfilePostViewSet
from profiles.views import PublicProfileViewSet
from rest_framework.routers import DefaultRouter


class AppRouter(DefaultRouter):
    def get_urls(self):
        return [
            *super().get_urls(),
            path("attachments/", include("attachments.urls")),
        ]


router = AppRouter(use_regex_path=False)
router.include_root_view = False
router.include_format_suffixes = settings.ENVIRONMENT == 'development'

router.register("authors", PublicProfileViewSet, basename="author")
router.register(
    "authors/<str:public_username>/posts",
    PublicProfilePostViewSet,
    basename="author-post",
)
