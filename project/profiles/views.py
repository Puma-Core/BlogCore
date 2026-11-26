from drf_spectacular.utils import extend_schema
from django.conf import settings
from rest_framework import mixins, viewsets

from profiles.models import PublicProfile
from profiles.serializers import PublicProfileSerializer

@extend_schema(exclude=settings.ENVIRONMENT == 'production')
class PublicProfileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = PublicProfile.objects.all()
    serializer_class = PublicProfileSerializer
    lookup_field = "public_username"
