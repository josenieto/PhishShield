import pytest

from infrastructure.config.api_defaults import (
    DEFAULT_MAX_UPLOAD_BYTES,
    MAX_UPLOAD_BYTES_ENV_VAR,
    ApiSettings,
    load_api_settings,
)


def test_should_load_default_api_settings_when_env_is_missing() -> None:
    assert load_api_settings({}) == ApiSettings(
        max_upload_bytes=DEFAULT_MAX_UPLOAD_BYTES
    )


def test_should_load_upload_limit_from_env() -> None:
    settings = load_api_settings({MAX_UPLOAD_BYTES_ENV_VAR: "2000000"})

    assert settings.max_upload_bytes == 2_000_000


def test_should_raise_error_when_upload_limit_is_not_an_integer() -> None:
    with pytest.raises(ValueError):
        load_api_settings({MAX_UPLOAD_BYTES_ENV_VAR: "abc"})


@pytest.mark.parametrize("value", ["0", "-1"])
def test_should_raise_error_when_upload_limit_is_zero_or_negative(
    value: str,
) -> None:
    with pytest.raises(ValueError):
        load_api_settings({MAX_UPLOAD_BYTES_ENV_VAR: value})
