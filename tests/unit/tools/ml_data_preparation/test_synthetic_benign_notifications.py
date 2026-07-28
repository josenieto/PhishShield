import pytest

from tools.ml_data_preparation.synthetic_benign_notifications import (
    NORMALIZED_LABEL_BENIGN,
    SYNTHETIC_BENIGN_NOTIFICATIONS_SOURCE,
    SYNTHETIC_BENIGN_NOTIFICATIONS_SOURCE_URI,
    iter_synthetic_benign_notification_templates,
    prepare_synthetic_benign_notification_template,
)


def test_should_generate_expected_number_of_templates() -> None:
    templates = iter_synthetic_benign_notification_templates(samples_per_category=2)

    assert len(templates) == 24
    assert {template.category for template in templates} == {
        "account_activity_summary",
        "account_usage_digest",
        "mfa_enabled_notice",
        "security_login_notice",
        "password_reset_confirmation",
        "newsletter_product_update",
        "account_preferences_update",
        "cloud_document_share_notice",
        "billing_receipt",
        "support_ticket_update",
        "hr_policy_update",
        "vendor_portal_notice",
    }


def test_should_reject_negative_sample_count() -> None:
    with pytest.raises(ValueError, match="samples_per_category must be greater than or equal to zero"):
        iter_synthetic_benign_notification_templates(samples_per_category=-1)


def test_should_prepare_template_as_benign_sample() -> None:
    template = iter_synthetic_benign_notification_templates(samples_per_category=1)[0]

    sample = prepare_synthetic_benign_notification_template(template)

    assert sample.source == SYNTHETIC_BENIGN_NOTIFICATIONS_SOURCE
    assert sample.source_uri == SYNTHETIC_BENIGN_NOTIFICATIONS_SOURCE_URI
    assert sample.original_label == "synthetic_benign"
    assert sample.normalized_label == NORMALIZED_LABEL_BENIGN
    assert sample.subject == template.subject
    assert sample.body_text == template.body_text
    assert sample.sender_domain == template.sender_domain
    assert sample.urls
    assert sample.attachment_filenames == ()
    assert sample.raw_available is False
    assert sample.metadata == {
        "category": template.category,
        "template_id": template.template_id,
        "original_label": "synthetic_benign",
    }


def test_should_build_stable_sample_id_for_same_template() -> None:
    template = iter_synthetic_benign_notification_templates(samples_per_category=1)[0]

    first_sample = prepare_synthetic_benign_notification_template(template)
    second_sample = prepare_synthetic_benign_notification_template(template)

    assert first_sample.sample_id == second_sample.sample_id
