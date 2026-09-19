from django.db import models
from django.db.models.functions import Substr


class PostQuerySet(models.QuerySet):
    def with_content_preview(self) -> models.QuerySet:
        return self.defer("content").annotate(
            content_preview=Substr("content", 1, 256),
        )
