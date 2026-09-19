from django.conf import settings
from posts.query_set import PostQuerySet
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from typing import cast

from posts.models import Post
from posts.serializers import PostDetailSerializer, PostListSerializer
from profiles.models import PublicProfile
from drf_spectacular.utils import extend_schema


@extend_schema(exclude=settings.ENVIRONMENT == 'production')
class PublicProfilePostViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    lookup_field = "unique_name"
    lookup_value_converter = "slug"

    def get_queryset(self):
        author = get_object_or_404(
            PublicProfile,
            public_username=self.kwargs["public_username"],
        )
        queryset = cast(
            PostQuerySet,
            Post.objects.filter(author=author).select_related("author"),
        )
        if self.action == "list":
            return queryset.with_content_preview().order_by("pk")
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostDetailSerializer
