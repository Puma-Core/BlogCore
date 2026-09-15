from django.forms import Textarea


class VditorWidget(Textarea):
    class Media:
        css = {"all": ("https://cdn.jsdelivr.net/npm/vditor@3.11.1/dist/index.css",)}
        js = (
            "https://cdn.jsdelivr.net/npm/vditor@3.11.1/dist/index.min.js",
            "posts/vditor.js",
        )

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["attrs"]["data-vditor"] = "true"
        return context
