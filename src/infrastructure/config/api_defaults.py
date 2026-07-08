from dataclasses import dataclass


DEFAULT_MAX_UPLOAD_BYTES = 1_000_000


@dataclass(frozen=True)
class ApiSettings:
    max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES


DEFAULT_API_SETTINGS = ApiSettings()
