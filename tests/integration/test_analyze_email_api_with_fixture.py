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
