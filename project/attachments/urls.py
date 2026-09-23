from django.urls import path

from attachments.views import AttachmentDetailView, AttachmentUploadView

urlpatterns = [
    path("upload/", AttachmentUploadView.as_view(), name="attachment-upload"),
    path("<uuid:pk>/", AttachmentDetailView.as_view(), name="attachment-detail"),
]
