from pathlib import Path

from fastapi.testclient import TestClient

from infrastructure.config.api_defaults import DEFAULT_API_SETTINGS
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
    assert payload["extracted_evidence"] == {
        "sender_domain": "example.zip",
        "subject": "Urgent account notice",
        "urls": ["https://example.com/login"],
        "attachment_filenames": [],
        "authentication_results": {
            "spf_result": "fail",
            "dkim_result": "pass",
            "dmarc_result": "fail",
        },
    }


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
    assert payload["extracted_evidence"] == {
        "sender_domain": "example.com",
        "subject": "Weekly account summary",
        "urls": [],
        "attachment_filenames": [],
        "authentication_results": {
            "spf_result": "pass",
            "dkim_result": "pass",
            "dmarc_result": "pass",
        },
    }


def test_should_keep_benign_newsletter_fixture_low_risk() -> None:
    client = TestClient(create_app())
    email_bytes = (_FIXTURES_DIR / "benign_newsletter_weekly_digest.eml").read_bytes()

    response = client.post(
        "/analyze-email",
        files={"file": ("benign_newsletter_weekly_digest.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["finding_codes"] == []
    assert payload["risk_score"]["risk_level"] == "LOW"
    assert payload["risk_score"]["has_critical_indicators"] is False
    assert payload["extracted_evidence"] == {
        "sender_domain": "updates.example.com",
        "subject": "Your weekly product digest",
        "urls": ["https://updates.example.com/blog/weekly-digest"],
        "attachment_filenames": [],
        "authentication_results": {
            "spf_result": "pass",
            "dkim_result": "pass",
            "dmarc_result": "pass",
        },
    }


def test_should_keep_benign_security_alert_fixture_without_critical_indicators() -> None:
    client = TestClient(create_app())
    email_bytes = (_FIXTURES_DIR / "benign_security_alert_login_notice.eml").read_bytes()

    response = client.post(
        "/analyze-email",
        files={"file": ("benign_security_alert_login_notice.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["risk_score"]["has_critical_indicators"] is False
    assert payload["risk_score"]["risk_level"] == "LOW"
    assert payload["extracted_evidence"] == {
        "sender_domain": "accounts.example.com",
        "subject": "New sign-in noticed on your account",
        "urls": ["https://accounts.example.com/security/activity"],
        "attachment_filenames": [],
        "authentication_results": {
            "spf_result": "pass",
            "dkim_result": "pass",
            "dmarc_result": "pass",
        },
    }


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
    assert payload["extracted_evidence"] == {
        "sender_domain": "example.com",
        "subject": "Invoice attached",
        "urls": [],
        "attachment_filenames": ["invoice.pdf.exe"],
        "authentication_results": {
            "spf_result": "pass",
            "dkim_result": "pass",
            "dmarc_result": "pass",
        },
    }


def test_should_flag_suspicious_password_reset_fixture() -> None:
    client = TestClient(create_app())
    email_bytes = (_FIXTURES_DIR / "suspicious_password_reset_portal.eml").read_bytes()

    response = client.post(
        "/analyze-email",
        files={"file": ("suspicious_password_reset_portal.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 200

    payload = response.json()

    assert "DOMAIN_HAS_SUSPICIOUS_TLD" in payload["finding_codes"]
    assert "URL_USES_KNOWN_SHORTENER_DOMAIN" in payload["finding_codes"]
    assert "AUTHENTICATION_DMARC_FAILED" in payload["finding_codes"]
    assert "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS" in payload["finding_codes"]
    assert payload["risk_score"]["risk_level"] in {"HIGH", "CRITICAL"}
    assert payload["risk_score"]["has_critical_indicators"] is True
    assert payload["extracted_evidence"] == {
        "sender_domain": "secure-account-portal.zip",
        "subject": "Urgent password reset required",
        "urls": ["https://bit.ly/secure-password-reset"],
        "attachment_filenames": [],
        "authentication_results": {
            "spf_result": "fail",
            "dkim_result": "pass",
            "dmarc_result": "fail",
        },
    }


def test_should_flag_suspicious_invoice_payment_fixture() -> None:
    client = TestClient(create_app())
    email_bytes = (_FIXTURES_DIR / "suspicious_invoice_payment_followup.eml").read_bytes()

    response = client.post(
        "/analyze-email",
        files={"file": ("suspicious_invoice_payment_followup.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 200

    payload = response.json()

    assert "ATTACHMENT_HAS_EXECUTABLE_EXTENSION" in payload["finding_codes"]
    assert "ATTACHMENT_HAS_DOUBLE_EXTENSION" in payload["finding_codes"]
    assert "SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS" in payload["finding_codes"]
    assert "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS" in payload["finding_codes"]
    assert payload["risk_score"]["risk_level"] in {"HIGH", "CRITICAL"}
    assert payload["risk_score"]["has_critical_indicators"] is True
    assert payload["extracted_evidence"] == {
        "sender_domain": "vendor-payments.example.com",
        "subject": "Invoice overdue - payment required today",
        "urls": [],
        "attachment_filenames": ["invoice_july_2026.pdf.exe"],
        "authentication_results": {
            "spf_result": "pass",
            "dkim_result": "pass",
            "dmarc_result": "pass",
        },
    }


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
    assert payload["extracted_evidence"] == {
        "sender_domain": "",
        "subject": "",
        "urls": ["https://example.com/login"],
        "attachment_filenames": [],
        "authentication_results": {
            "spf_result": "unknown",
            "dkim_result": "unknown",
            "dmarc_result": "unknown",
        },
    }


def test_should_degrade_safely_for_malformed_multipart_uploaded_eml_fixture() -> None:
    client = TestClient(create_app())
    email_bytes = (
        _FIXTURES_DIR / "malformed_multipart_missing_closing_boundary.eml"
    ).read_bytes()

    response = client.post(
        "/analyze-email",
        files={
            "file": (
                "malformed_multipart_missing_closing_boundary.eml",
                email_bytes,
                "message/rfc822",
            )
        },
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
    assert payload["extracted_evidence"]["authentication_results"] == {
        "spf_result": "unknown",
        "dkim_result": "unknown",
        "dmarc_result": "unknown",
    }


def test_should_return_413_for_oversized_uploaded_eml_fixture() -> None:
    client = TestClient(create_app())
    oversized_email = b"x" * (DEFAULT_API_SETTINGS.max_upload_bytes + 1)

    response = client.post(
        "/analyze-email",
        files={"file": ("oversized.eml", oversized_email, "message/rfc822")},
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "Uploaded email exceeds maximum allowed size."
    }


def test_should_return_422_for_unexpected_analysis_failure(
    monkeypatch,
) -> None:
    class FailingAnalyzeRawEmailUseCase:
        def execute(self, command):
            raise ValueError("boom")

    monkeypatch.setattr(
        "infrastructure.entrypoints.api.routers.analyze_email._build_analyze_raw_email_use_case",
        lambda: FailingAnalyzeRawEmailUseCase(),
    )

    client = TestClient(create_app())
    email_bytes = (_FIXTURES_DIR / "benign_account_summary.eml").read_bytes()

    response = client.post(
        "/analyze-email",
        files={"file": ("benign_account_summary.eml", email_bytes, "message/rfc822")},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Uploaded email could not be analyzed."
    }
