from rest_framework import serializers

from profiles.models import PublicProfile, SocialNetworkInstance


class SocialNetworkInstanceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="config.name", read_only=True)
    url = serializers.CharField(read_only=True, allow_null=True)
    icon_url = serializers.CharField(read_only=True)

    class Meta:
        model = SocialNetworkInstance
        fields = ("name", "url", "icon_url")


class PublicProfileSerializer(serializers.ModelSerializer):
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
            "fullname",
            "social_networks",
        )

    fullname = serializers.SerializerMethodField()
    social_networks = serializers.SerializerMethodField()

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_social_networks(self, obj):
        if not obj.pk:
            return []
        return SocialNetworkInstanceSerializer(
            obj.social_networks,
            many=True,
        ).data
