from uuid import UUID, uuid4

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from attachments.models import Attachment, attachment_upload_to


def test_attachment_metadata_defaults_to_an_empty_object() -> None:
    attachment = Attachment()

    assert attachment.metadata == {}


def test_attachment_metadata_defaults_are_not_shared() -> None:
    first = Attachment()
    second = Attachment()

    first.metadata["relationship"] = {"posts": [1]}

    assert second.metadata == {}


def test_attachment_uses_a_generated_uuid_as_its_primary_key() -> None:
    attachment = Attachment()
    identifier = Attachment._meta.get_field("id")

    assert isinstance(attachment.id, UUID)
    assert identifier.primary_key is True
    assert identifier.editable is False


def test_attachment_field_contract() -> None:
    file = Attachment._meta.get_field("file")
    original_name = Attachment._meta.get_field("original_name")
    mime_type = Attachment._meta.get_field("mime_type")
    size = Attachment._meta.get_field("size")
    metadata = Attachment._meta.get_field("metadata")
    created_at = Attachment._meta.get_field("created_at")
    updated_at = Attachment._meta.get_field("updated_at")

    assert isinstance(file, models.FileField)
    assert file.upload_to is attachment_upload_to
    assert original_name.max_length == 255
    assert mime_type.max_length == 127
    assert isinstance(size, models.PositiveBigIntegerField)
    assert metadata.default is dict
    assert metadata.blank is True
    assert created_at.auto_now_add is True
    assert updated_at.auto_now is True


def test_attachment_owner_targets_the_configured_user_model() -> None:
    owner = Attachment._meta.get_field("owner")

    assert owner.related_model is get_user_model()
    assert owner.remote_field.on_delete is models.CASCADE
    assert owner.remote_field.related_name == "attachments"


def test_attachment_has_no_post_relation() -> None:
    field_names = {field.name for field in Attachment._meta.get_fields()}

    assert "post" not in field_names


def test_attachment_indexes_owner_and_creation_time() -> None:
    assert len(Attachment._meta.indexes) == 1
    assert Attachment._meta.indexes[0].fields == ["owner", "created_at"]


def test_attachment_upload_path_uses_its_uuid_and_file_extension() -> None:
    attachment = Attachment(id=uuid4())

    path = attachment_upload_to(attachment, "My Photo.WEBP")

    assert path == f"attachments/{attachment.id}.webp"


def test_attachment_upload_path_does_not_use_the_original_filename() -> None:
    attachment = Attachment(id=uuid4())

    path = attachment_upload_to(attachment, "../../unsafe name.jpg")

    assert path == f"attachments/{attachment.id}.jpg"


def test_attachments_with_the_same_name_have_different_storage_paths() -> None:
    first = Attachment(id=uuid4())
    second = Attachment(id=uuid4())

    assert attachment_upload_to(first, "photo.jpeg") != attachment_upload_to(
        second, "photo.jpeg"
    )


def test_attachment_metadata_preserves_dynamic_post_references() -> None:
    metadata = {"relationship": {"posts": [1]}}
    attachment = Attachment(metadata=metadata)

    attachment.clean()

    assert attachment.metadata == metadata


@pytest.mark.parametrize("metadata", (["not", "an", "object"], "invalid", None))
def test_attachment_rejects_non_object_metadata(metadata) -> None:
    attachment = Attachment(metadata=metadata)

    with pytest.raises(ValidationError, match="Metadata must be a JSON object"):
        attachment.clean()


def test_attachment_string_representation_is_the_original_name() -> None:
    attachment = Attachment(original_name="cover.webp")

    assert str(attachment) == "cover.webp"
