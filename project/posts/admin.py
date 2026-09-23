from django.contrib import admin

from .forms import PostForm
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostForm
    list_display = ("title", "author", "created_at")
    list_select_related = ("author",)
