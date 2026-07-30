import json
from pathlib import Path

import joblib
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
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


def test_should_include_model_assessment_route() -> None:
    app = create_app()
    route_paths = set(app.openapi()["paths"])

    assert "/analyze-email-model-assessment" in route_paths


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
    assert payload["extracted_evidence"]["sender_domain"] == "xn--paypl-3ve.zip"
    assert payload["extracted_evidence"]["authentication_results"] == {
        "spf_result": "fail",
        "dkim_result": "pass",
        "dmarc_result": "fail",
    }


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


def test_should_wire_configured_model_assessment_through_app_factory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    model_path, metadata_path = _write_model_and_metadata(tmp_path)
    monkeypatch.setenv("PHISHSHIELD_MODEL_ASSESSMENT_ENABLED", "true")
    monkeypatch.setenv("PHISHSHIELD_MODEL_ARTIFACT_PATH", str(model_path))
    monkeypatch.setenv("PHISHSHIELD_MODEL_METADATA_PATH", str(metadata_path))

    client = TestClient(create_app())
    email_bytes = b"\r\n".join(
        [
            b"From: Security <security@example.com>",
            b"Subject: Verify your account",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Confirm your login at https://example.net/login.",
        ]
    )

    model_response = client.post(
        "/analyze-email-model-assessment",
        files={"file": ("sample.eml", email_bytes, "message/rfc822")},
    )
    deterministic_response = client.post(
        "/analyze-email",
        files={"file": ("sample.eml", email_bytes, "message/rfc822")},
    )

    assert model_response.status_code == 200
    model_assessment = model_response.json()["model_assessment"]
    assert model_assessment["status"] == "completed"
    assert model_assessment["model_name"] == "app-factory-test-model"
    assert model_assessment["model_version"] == "app-factory-test-commit"

    assert deterministic_response.status_code == 200
    assert "risk_score" in deterministic_response.json()


def _write_model_and_metadata(tmp_path: Path) -> tuple[Path, Path]:
    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("classifier", LogisticRegression(max_iter=1_000)),
        ]
    )
    model.fit(
        [
            "Account activity summary is ready.",
            "Newsletter preferences were updated.",
            "Verify your account password now.",
            "Confirm your login to keep access.",
        ],
        ["benign", "benign", "suspicious", "suspicious"],
    )
    model_path = tmp_path / "model.joblib"
    metadata_path = tmp_path / "metadata.json"
    joblib.dump(model, model_path)
    metadata_path.write_text(
        json.dumps(
            {
                "model_name": "app-factory-test-model",
                "git_commit": "app-factory-test-commit",
                "feature_set": "text_with_light_metadata",
            }
        ),
        encoding="utf-8",
    )

    return model_path, metadata_path
