import pytest

from infrastructure.entrypoints.upload_limits import (
    UploadSizeLimitExceeded,
    enforce_upload_size,
)


def test_should_accept_email_at_configured_limit() -> None:
    email_bytes = b"12345"

    assert enforce_upload_size(email_bytes, max_bytes=5) == email_bytes


def test_should_reject_email_above_configured_limit() -> None:
    with pytest.raises(UploadSizeLimitExceeded):
        enforce_upload_size(b"123456", max_bytes=5)
