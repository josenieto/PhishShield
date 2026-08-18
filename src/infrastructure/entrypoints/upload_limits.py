"""Shared upload-size enforcement for all application entrypoints."""

from fastapi import UploadFile


class UploadSizeLimitExceeded(ValueError):
    """Raised when an uploaded email exceeds the configured byte limit."""


def enforce_upload_size(email_bytes: bytes, max_bytes: int) -> bytes:
    if len(email_bytes) > max_bytes:
        raise UploadSizeLimitExceeded

    return email_bytes


async def read_upload_file_with_limit(file: UploadFile, max_bytes: int) -> bytes:
    email_bytes = await file.read(max_bytes + 1)
    return enforce_upload_size(email_bytes, max_bytes)
