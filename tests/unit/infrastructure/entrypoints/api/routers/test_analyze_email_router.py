from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from infrastructure.config.api_defaults import ApiSettings, DEFAULT_API_SETTINGS
from infrastructure.entrypoints.api.routers.analyze_email import router


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
    oversized_email = b"x" * (DEFAULT_API_SETTINGS.max_upload_bytes + 1)

    response = client.post(
        "/analyze-email",
        files={"file": ("oversized.eml", oversized_email, "message/rfc822")},
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "Uploaded email exceeds maximum allowed size."
    }


def test_should_return_422_when_email_analysis_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingAnalyzeRawEmailUseCase:
        def execute(self, command):
            raise ValueError("boom")

    monkeypatch.setattr(
        "infrastructure.entrypoints.api.routers.analyze_email._build_analyze_raw_email_use_case",
        lambda: FailingAnalyzeRawEmailUseCase(),
    )

    client = _client()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Broken",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Body.",
        ]
    )

    response = client.post(
        "/analyze-email",
        files={"file": ("broken.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Uploaded email could not be analyzed."
    }


def test_should_use_configured_upload_limit_from_app_state() -> None:
    app = FastAPI()
    app.state.api_settings = ApiSettings(max_upload_bytes=5)
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/analyze-email",
        files={"file": ("oversized.eml", b"123456", "message/rfc822")},
    )

    assert response.status_code == 413


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)

    return TestClient(app)
