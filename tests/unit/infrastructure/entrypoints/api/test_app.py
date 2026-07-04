from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.entrypoints.api.app import create_app


def test_should_create_fastapi_app() -> None:
    app = create_app()

    assert isinstance(app, FastAPI)
    assert app.title == "PhishShield"


def test_should_include_analyze_email_route() -> None:
    app = create_app()
    route_paths = set(app.openapi()["paths"])

    assert "/analyze-email" in route_paths


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
