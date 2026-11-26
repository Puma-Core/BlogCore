from django.forms import ModelForm

from posts.models import Post
from posts.widgets import VditorWidget


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
        widgets = {"content": VditorWidget}
