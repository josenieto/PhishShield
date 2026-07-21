from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from infrastructure.config.api_defaults import ApiSettings, DEFAULT_API_SETTINGS
from infrastructure.entrypoints.api.routers.model_assessment import router


def test_should_return_not_configured_model_assessment_for_uploaded_email() -> None:
    client = _client()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Advisory assessment",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Please review your account activity.",
        ]
    )

    response = client.post(
        "/analyze-email-model-assessment",
        files={"file": ("sample.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "model_assessment": {
            "status": "not_configured",
            "label": "unknown",
            "confidence": None,
            "summary": "",
            "signals": [],
            "model_name": "",
            "model_version": "",
            "error_message": "",
        }
    }


def test_should_reject_oversized_uploaded_email_for_model_assessment() -> None:
    client = _client()
    oversized_email = b"x" * (DEFAULT_API_SETTINGS.max_upload_bytes + 1)

    response = client.post(
        "/analyze-email-model-assessment",
        files={"file": ("oversized.eml", oversized_email, "message/rfc822")},
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "Uploaded email exceeds maximum allowed size."
    }


def test_should_return_422_when_model_assessment_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingAssessRawEmailWithModelUseCase:
        def execute(self, command):
            raise ValueError("boom")

    monkeypatch.setattr(
        "infrastructure.entrypoints.api.routers.model_assessment._build_assess_raw_email_with_model_use_case",
        lambda: FailingAssessRawEmailWithModelUseCase(),
    )

    client = _client()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Broken assessment",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Body.",
        ]
    )

    response = client.post(
        "/analyze-email-model-assessment",
        files={"file": ("broken.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Uploaded email could not be assessed by the model."
    }


def test_should_use_configured_upload_limit_from_app_state() -> None:
    app = FastAPI()
    app.state.api_settings = ApiSettings(max_upload_bytes=5)
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/analyze-email-model-assessment",
        files={"file": ("oversized.eml", b"123456", "message/rfc822")},
    )

    assert response.status_code == 413


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)

    return TestClient(app)
