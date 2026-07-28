import pytest

from tools.ml_data_preparation.synthetic_suspicious_notifications import (
    NORMALIZED_LABEL_SUSPICIOUS,
    SYNTHETIC_SUSPICIOUS_NOTIFICATIONS_SOURCE,
    SYNTHETIC_SUSPICIOUS_NOTIFICATIONS_SOURCE_URI,
    iter_synthetic_suspicious_notification_templates,
    prepare_synthetic_suspicious_notification_template,
)


def test_should_generate_expected_number_of_templates() -> None:
    templates = iter_synthetic_suspicious_notification_templates(samples_per_category=2)

    assert len(templates) == 24
    assert {template.category for template in templates} == {
        "account_activity_verification_lure",
        "account_usage_suspension_lure",
        "mfa_push_approval_lure",
        "security_login_verification_lure",
        "password_reset_portal_lure",
        "newsletter_account_preferences_lure",
        "cloud_document_review_lure",
        "billing_payment_confirmation_lure",
        "support_ticket_credential_lure",
        "hr_policy_acknowledgement_lure",
        "vendor_portal_reauthentication_lure",
        "storage_quota_verification_lure",
    }


def test_should_reject_negative_sample_count() -> None:
    with pytest.raises(ValueError, match="samples_per_category must be greater than or equal to zero"):
        iter_synthetic_suspicious_notification_templates(samples_per_category=-1)


def test_should_prepare_template_as_suspicious_sample() -> None:
    template = iter_synthetic_suspicious_notification_templates(samples_per_category=1)[0]

    sample = prepare_synthetic_suspicious_notification_template(template)

    assert sample.source == SYNTHETIC_SUSPICIOUS_NOTIFICATIONS_SOURCE
    assert sample.source_uri == SYNTHETIC_SUSPICIOUS_NOTIFICATIONS_SOURCE_URI
    assert sample.original_label == "synthetic_suspicious"
    assert sample.normalized_label == NORMALIZED_LABEL_SUSPICIOUS
    assert sample.subject == template.subject
    assert sample.body_text == template.body_text
    assert sample.sender_domain == template.sender_domain
    assert sample.urls
    assert sample.attachment_filenames == ()
    assert sample.raw_available is False
    assert sample.metadata == {
        "category": template.category,
        "template_id": template.template_id,
        "original_label": "synthetic_suspicious",
    }


def test_should_build_stable_sample_id_for_same_template() -> None:
    template = iter_synthetic_suspicious_notification_templates(samples_per_category=1)[0]

    first_sample = prepare_synthetic_suspicious_notification_template(template)
    second_sample = prepare_synthetic_suspicious_notification_template(template)

    assert first_sample.sample_id == second_sample.sample_id
