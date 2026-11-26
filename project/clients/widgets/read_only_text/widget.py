from django.utils.html import format_html
from django import forms

class ReadOnlyTextWidget(forms.Widget):
    template_name = "project/clients/widgets/read_only_text/widget.html"

    def __init__(self, tag="div", copy_button=False, attrs=None):
        self.display_tag = tag
        self.copy_button = copy_button
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["display_tag"] = self.display_tag
        context["widget"]["copy_button"] = self.copy_button
        return context