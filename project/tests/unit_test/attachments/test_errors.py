import pytest
from rest_framework.exceptions import ErrorDetail, ValidationError

from attachments.errors import (
    AttachmentTooLargeError,
    InvalidAttachmentMetadataError,
    InvalidAttachmentMetadataJsonError,
    MissingAttachmentFileError,
    UnsupportedAttachmentMediaTypeError,
)


@pytest.mark.parametrize(
    ("error_class", "field", "message"),
    (
        (MissingAttachmentFileError, "file", "An image file is required."),
        (
            UnsupportedAttachmentMediaTypeError,
            "file",
            "Only JPEG/JPG and WebP images are allowed.",
        ),
        (AttachmentTooLargeError, "file", "The image exceeds the maximum upload size."),
        (
            InvalidAttachmentMetadataJsonError,
            "metadata",
            "Metadata must be valid JSON.",
        ),
        (
            InvalidAttachmentMetadataError,
            "metadata",
            "Metadata must be a JSON object.",
        ),
    ),
)
def test_attachment_validation_errors_provide_their_field_and_message(
    error_class, field, message
) -> None:
    error = error_class()

    assert isinstance(error, ValidationError)
    assert error.detail == {field: ErrorDetail(message, code="invalid")}
