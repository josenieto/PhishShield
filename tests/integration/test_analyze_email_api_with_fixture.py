from pathlib import Path

from fastapi.testclient import TestClient

from infrastructure.entrypoints.api.app import create_app


_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "emails"


def test_should_analyze_uploaded_suspicious_eml_fixture() -> None:
    client = TestClient(create_app())
    email_bytes = (_FIXTURES_DIR / "suspicious_html_notice.eml").read_bytes()

    response = client.post(
        "/analyze-email",
        files={"file": ("suspicious_html_notice.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 200

    payload = response.json()

    assert "DOMAIN_HAS_SUSPICIOUS_TLD" in payload["finding_codes"]
    assert "AUTHENTICATION_SPF_FAILED" in payload["finding_codes"]
    assert "AUTHENTICATION_DMARC_FAILED" in payload["finding_codes"]
    assert "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS" in payload["finding_codes"]
    assert "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS" in payload["finding_codes"]
    assert payload["finding_summary"]["highest_severity"] == "CRITICAL"
    assert payload["risk_score"]["risk_level"] == "CRITICAL"
    assert payload["risk_score"]["has_critical_indicators"] is True


def test_should_analyze_uploaded_benign_eml_fixture() -> None:
    client = TestClient(create_app())
    email_bytes = (_FIXTURES_DIR / "benign_account_summary.eml").read_bytes()

    response = client.post(
        "/analyze-email",
        files={"file": ("benign_account_summary.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["finding_codes"] == []
    assert payload["unique_finding_codes"] == []
    assert payload["finding_summary"]["total_findings"] == 0
    assert payload["finding_summary"]["highest_severity"] == "UNKNOWN"
    assert payload["risk_score"]["raw_score"] == 0
    assert payload["risk_score"]["capped_score"] == 0
    assert payload["risk_score"]["risk_level"] == "LOW"
    assert payload["risk_score"]["has_critical_indicators"] is False


def test_should_analyze_uploaded_suspicious_attachment_eml_fixture() -> None:
    client = TestClient(create_app())
    email_bytes = (_FIXTURES_DIR / "suspicious_attachment.eml").read_bytes()

    response = client.post(
        "/analyze-email",
        files={"file": ("suspicious_attachment.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 200

    payload = response.json()

    assert "ATTACHMENT_HAS_EXECUTABLE_EXTENSION" in payload["finding_codes"]
    assert "ATTACHMENT_HAS_DOUBLE_EXTENSION" in payload["finding_codes"]
    assert payload["finding_summary"]["highest_severity"] == "CRITICAL"
    assert payload["risk_score"]["raw_score"] == 70
    assert payload["risk_score"]["capped_score"] == 70
    assert payload["risk_score"]["risk_level"] == "HIGH"
    assert payload["risk_score"]["has_critical_indicators"] is True


def test_should_degrade_safely_for_malformed_uploaded_eml_fixture() -> None:
    client = TestClient(create_app())
    email_bytes = (_FIXTURES_DIR / "malformed_missing_headers.eml").read_bytes()

    response = client.post(
        "/analyze-email",
        files={"file": ("malformed_missing_headers.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["finding_codes"] == ["AUTHENTICATION_RESULTS_UNKNOWN"]
    assert payload["unique_finding_codes"] == ["AUTHENTICATION_RESULTS_UNKNOWN"]
    assert payload["finding_summary"]["highest_severity"] == "MEDIUM"
    assert payload["finding_summary"]["total_findings"] == 1
    assert payload["risk_score"]["raw_score"] == 15
    assert payload["risk_score"]["capped_score"] == 15
    assert payload["risk_score"]["risk_level"] == "LOW"
    assert payload["risk_score"]["has_critical_indicators"] is False
