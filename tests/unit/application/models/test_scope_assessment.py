from application.models.extracted_email import ExtractedEmailContent
from application.models.scope_assessment import (
    SCOPE_FAMILY_ACCOUNT,
    SCOPE_FAMILY_OUT_OF_SCOPE,
    SCOPE_REASON_NO_FAMILY_SIGNAL,
    SCOPE_REASON_URL_ONLY,
    assess_email_scope,
)


def test_should_assign_account_family_from_notification_terms() -> None:
    result = assess_email_scope(_email("Account activity summary", "Review your account sign in history."))

    assert result.family == SCOPE_FAMILY_ACCOUNT
    assert result.confidence > 0.0


def test_should_reject_url_only_content() -> None:
    result = assess_email_scope(_email("", "https://example.test/login"))

    assert result.family == SCOPE_FAMILY_OUT_OF_SCOPE
    assert result.reason == SCOPE_REASON_URL_ONLY


def test_should_reject_content_without_validated_family_signal() -> None:
    result = assess_email_scope(_email("Team update", "The project meeting moved to Friday."))

    assert result.family == SCOPE_FAMILY_OUT_OF_SCOPE
    assert result.reason == SCOPE_REASON_NO_FAMILY_SIGNAL


def _email(subject: str, body: str) -> ExtractedEmailContent:
    return ExtractedEmailContent("example.com", (), (), subject, body, "unknown", "unknown", "unknown")
