import json
import logging

from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attachments.errors import (
    AttachmentTooLargeError,
    InvalidAttachmentMetadataError,
    InvalidAttachmentMetadataJsonError,
    MissingAttachmentFileError,
    UnsupportedAttachmentMediaTypeError,
)
from attachments.models import Attachment


logger = logging.getLogger(__name__)


@extend_schema(exclude=settings.ENVIRONMENT == 'production')
class AttachmentUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        uploaded_file = request.FILES.get("file")
        if uploaded_file is None:
            raise MissingAttachmentFileError()
        if uploaded_file.content_type not in settings.POST_ATTACHMENT_ALLOWED_MIME_TYPES:
            raise UnsupportedAttachmentMediaTypeError()
        if uploaded_file.size > settings.POST_ATTACHMENT_MAX_SIZE:
            raise AttachmentTooLargeError()

        metadata = self._metadata(request.data.get("metadata"))
        attachment = Attachment(
            file=uploaded_file,
            original_name=uploaded_file.name,
            mime_type=uploaded_file.content_type,
            size=uploaded_file.size,
            metadata=metadata,
            owner=request.user,
        )
        attachment.full_clean()
        try:
            attachment.file.save(uploaded_file.name, uploaded_file, save=False)
        except Exception:
            logger.exception(
                "Attachment file upload failed",
                extra={
                    "storage_backend": settings.STORAGES["default"]["BACKEND"],
                    "attachment_name": attachment.file.name,
                },
            )
            raise

        try:
            attachment.save()
        except Exception:
            logger.exception(
                "Attachment record creation failed",
                extra={"attachment_name": attachment.file.name},
            )
            try:
                attachment.file.delete(save=False)
            except Exception:
                logger.exception(
                    "Attachment storage cleanup failed",
                    extra={"attachment_name": attachment.file.name},
                )
            raise

        url = request.build_absolute_uri(attachment.file.url)

        return Response(
            {
                "code": 0,
                "msg": "",
                "data": {
                    "id": str(attachment.id),
                    "url": url,
                    "errFiles": [],
                    "succMap": {attachment.original_name: url},
                },
            },
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _metadata(value):
        if value in (None, ""):
            return {}
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise InvalidAttachmentMetadataJsonError() from exc
        if not isinstance(value, dict):
            raise InvalidAttachmentMetadataError()
        return value

@extend_schema(exclude=settings.ENVIRONMENT == 'production')
class AttachmentDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        attachment = self._attachment(request, pk)
        return Response(
            {
                "id": str(attachment.id),
                "url": request.build_absolute_uri(attachment.file.url),
                "original_name": attachment.original_name,
                "mime_type": attachment.mime_type,
                "size": attachment.size,
                "metadata": attachment.metadata,
            }
        )

    def delete(self, request, pk):
        attachment = self._attachment(request, pk)
        attachment.file.delete(save=False)
        attachment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _attachment(request, pk):
        return get_object_or_404(Attachment, pk=pk, owner=request.user)
