from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.entrypoints.api.routers.analyze_email import (
    _DEFAULT_MAX_UPLOAD_BYTES,
    router,
)


def test_should_analyze_uploaded_plain_text_email() -> None:
    client = _client()
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
    assert "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS" in payload["finding_codes"]
    assert payload["finding_summary"]["highest_severity"] == "CRITICAL"
    assert payload["risk_score"]["has_critical_indicators"] is True


def test_should_analyze_uploaded_html_email() -> None:
    client = _client()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.zip>",
            b"Subject: =?utf-8?q?Urgent_account_notice?=",
            b"Content-Type: text/html; charset=utf-8",
            b"",
            b"<html><body>Please verify your account at https://example.com/login.</body></html>",
        ]
    )

    response = client.post(
        "/analyze-email",
        files={"file": ("sample.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "DOMAIN_HAS_SUSPICIOUS_TLD" in payload["finding_codes"]
    assert "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS" in payload["finding_codes"]
    assert "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS" in payload["finding_codes"]


def test_should_return_response_for_empty_uploaded_email() -> None:
    client = _client()

    response = client.post(
        "/analyze-email",
        files={"file": ("empty.eml", b"", "message/rfc822")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["finding_codes"] == ["AUTHENTICATION_RESULTS_UNKNOWN"]
    assert payload["finding_summary"]["total_findings"] == 1


def test_should_reject_oversized_uploaded_email() -> None:
    client = _client()
    oversized_email = b"x" * (_DEFAULT_MAX_UPLOAD_BYTES + 1)

    response = client.post(
        "/analyze-email",
        files={"file": ("oversized.eml", oversized_email, "message/rfc822")},
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "Uploaded email exceeds maximum allowed size."
    }


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)

    return TestClient(app)
