from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def attachment_upload_to(instance: "Attachment", filename: str) -> str:
    return f"attachments/{instance.id}{Path(filename).suffix.lower()}"


class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    file = models.FileField(upload_to=attachment_upload_to)
    original_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=127)
    size = models.PositiveBigIntegerField()
    metadata = models.JSONField(default=dict, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=("owner", "created_at"))]

    def clean(self) -> None:
        super().clean()
        if not isinstance(self.metadata, dict):
            raise ValidationError({"metadata": "Metadata must be a JSON object."})

    def __str__(self) -> str:
        return self.original_name
