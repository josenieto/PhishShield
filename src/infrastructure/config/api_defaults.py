import os
from collections.abc import Mapping
from dataclasses import dataclass


DEFAULT_MAX_UPLOAD_BYTES = 1_000_000
MAX_UPLOAD_BYTES_ENV_VAR = "PHISHSHIELD_MAX_UPLOAD_BYTES"
MODEL_ASSESSMENT_ENABLED_ENV_VAR = "PHISHSHIELD_MODEL_ASSESSMENT_ENABLED"
MODEL_ARTIFACT_PATH_ENV_VAR = "PHISHSHIELD_MODEL_ARTIFACT_PATH"
MODEL_METADATA_PATH_ENV_VAR = "PHISHSHIELD_MODEL_METADATA_PATH"


@dataclass(frozen=True)
class ApiSettings:
    max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES
    model_assessment_enabled: bool = False
    model_artifact_path: str = ""
    model_metadata_path: str = ""


def load_api_settings(environ: Mapping[str, str] | None = None) -> ApiSettings:
    source = os.environ if environ is None else environ
    raw_max_upload_bytes = source.get(MAX_UPLOAD_BYTES_ENV_VAR)
    model_assessment_enabled = _parse_bool(source.get(MODEL_ASSESSMENT_ENABLED_ENV_VAR))
    model_artifact_path = source.get(MODEL_ARTIFACT_PATH_ENV_VAR, "")
    model_metadata_path = source.get(MODEL_METADATA_PATH_ENV_VAR, "")

    if raw_max_upload_bytes is None:
        return ApiSettings(
            model_assessment_enabled=model_assessment_enabled,
            model_artifact_path=model_artifact_path,
            model_metadata_path=model_metadata_path,
        )

    max_upload_bytes = int(raw_max_upload_bytes)

    if max_upload_bytes <= 0:
        raise ValueError("PHISHSHIELD_MAX_UPLOAD_BYTES must be greater than zero")

    return ApiSettings(
        max_upload_bytes=max_upload_bytes,
        model_assessment_enabled=model_assessment_enabled,
        model_artifact_path=model_artifact_path,
        model_metadata_path=model_metadata_path,
    )


def _parse_bool(raw_value: str | None) -> bool:
    if raw_value is None:
        return False

    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


DEFAULT_API_SETTINGS = ApiSettings()
