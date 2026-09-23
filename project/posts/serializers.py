from rest_framework import serializers

from posts.models import Post


class PostListSerializer(serializers.ModelSerializer):
    content_preview = serializers.CharField(read_only=True)
    author_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "unique_name",
            "title",
            "content_preview",
            "created_at",
            "author_full_name",
        )

    def get_author_full_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"


class PostDetailSerializer(serializers.ModelSerializer):
    public_username = serializers.CharField(
        source="author.public_username",
        read_only=True,
    )
    author_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "unique_name",
            "title",
            "content",
            "created_at",
            "updated_at",
            "public_username",
            "author_full_name",
        )

    def get_author_full_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"
