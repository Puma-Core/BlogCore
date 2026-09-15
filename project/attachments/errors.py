from rest_framework.exceptions import ValidationError


class AttachmentValidationError(ValidationError):
    field: str
    message: str

    def __init__(self) -> None:
        super().__init__({self.field: self.message})


class MissingAttachmentFileError(AttachmentValidationError):
    field = "file"
    message = "An image file is required."


class UnsupportedAttachmentMediaTypeError(AttachmentValidationError):
    field = "file"
    message = "Only JPEG/JPG and WebP images are allowed."


class AttachmentTooLargeError(AttachmentValidationError):
    field = "file"
    message = "The image exceeds the maximum upload size."


class InvalidAttachmentMetadataJsonError(AttachmentValidationError):
    field = "metadata"
    message = "Metadata must be valid JSON."


class InvalidAttachmentMetadataError(AttachmentValidationError):
    field = "metadata"
    message = "Metadata must be a JSON object."
