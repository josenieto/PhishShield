import os
from collections.abc import Mapping
from dataclasses import dataclass


DEFAULT_MAX_UPLOAD_BYTES = 1_000_000
MAX_UPLOAD_BYTES_ENV_VAR = "PHISHSHIELD_MAX_UPLOAD_BYTES"


@dataclass(frozen=True)
class ApiSettings:
    max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES


def load_api_settings(environ: Mapping[str, str] | None = None) -> ApiSettings:
    source = os.environ if environ is None else environ
    raw_max_upload_bytes = source.get(MAX_UPLOAD_BYTES_ENV_VAR)

    if raw_max_upload_bytes is None:
        return ApiSettings()

    max_upload_bytes = int(raw_max_upload_bytes)

    if max_upload_bytes <= 0:
        raise ValueError("PHISHSHIELD_MAX_UPLOAD_BYTES must be greater than zero")

    return ApiSettings(max_upload_bytes=max_upload_bytes)


DEFAULT_API_SETTINGS = ApiSettings()
