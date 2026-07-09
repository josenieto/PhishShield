from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from infrastructure.entrypoints.api.app import create_app


def test_should_create_fastapi_app() -> None:
    app = create_app()

    assert isinstance(app, FastAPI)
    assert app.title == "PhishShield"


def test_should_include_analyze_email_route() -> None:
    app = create_app()
    route_paths = set(app.openapi()["paths"])

    assert "/analyze-email" in route_paths


def test_should_include_health_route() -> None:
    app = create_app()
    route_paths = set(app.openapi()["paths"])

    assert "/health" in route_paths


def test_should_analyze_email_through_created_app() -> None:
    client = TestClient(create_app())
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@xn--paypl-3ve.zip>",
            b"Subject: Urgent account notice",
            b"Authentication-Results: mx.example.com; spf=fail smtp.mailfrom=bad.example; dkim=pass header.d=example.com; dmarc=fail header.from=example.com",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Please verify your account at https://example.com/login.",
        ]
    )

    response = client.post(
        "/analyze-email",
        files={"file": ("sample.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "DOMAIN_CONTAINS_PUNYCODE" in payload["finding_codes"]
    assert "AUTHENTICATION_DMARC_FAILED" in payload["finding_codes"]
    assert payload["finding_summary"]["highest_severity"] == "CRITICAL"


def test_should_return_health_response_through_created_app() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_should_load_api_settings_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PHISHSHIELD_MAX_UPLOAD_BYTES", "123")

    app = create_app()

    assert app.state.api_settings.max_upload_bytes == 123


def test_should_raise_error_when_api_settings_are_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PHISHSHIELD_MAX_UPLOAD_BYTES", "0")

    with pytest.raises(ValueError):
        create_app()
