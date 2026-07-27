import pytest

from tools.ml_data_preparation.phishing_email_detection import (
    NORMALIZED_LABEL_BENIGN,
    NORMALIZED_LABEL_SUSPICIOUS,
    PHISHING_EMAIL_DETECTION_SOURCE,
    PHISHING_EMAIL_DETECTION_SOURCE_URI,
    normalize_phishing_email_detection_label,
    prepare_phishing_email_detection_row,
)


def test_should_normalize_safe_email_label_as_benign() -> None:
    assert normalize_phishing_email_detection_label("Safe Email") == NORMALIZED_LABEL_BENIGN


def test_should_normalize_phishing_email_label_as_suspicious() -> None:
    assert normalize_phishing_email_detection_label("Phishing Email") == NORMALIZED_LABEL_SUSPICIOUS


def test_should_reject_unknown_label() -> None:
    with pytest.raises(ValueError, match="Unsupported Phishing Email Detection label"):
        normalize_phishing_email_detection_label("Spam Email")


def test_should_prepare_safe_email_sample() -> None:
    sample = prepare_phishing_email_detection_row(
        email_text="Your invoice is available at https://example.com/invoice.",
        source_id="csv-1",
        original_label="Safe Email",
        csv_row_number=2,
    )

    assert sample.source == PHISHING_EMAIL_DETECTION_SOURCE
    assert sample.source_id == "csv-1"
    assert sample.source_uri == PHISHING_EMAIL_DETECTION_SOURCE_URI
    assert sample.original_label == "Safe Email"
    assert sample.normalized_label == NORMALIZED_LABEL_BENIGN
    assert sample.subject == ""
    assert sample.body_text == "Your invoice is available at https://example.com/invoice."
    assert sample.sender_domain == ""
    assert sample.urls == ("https://example.com/invoice",)
    assert sample.attachment_filenames == ()
    assert sample.raw_available is False
    assert sample.metadata == {"original_label": "Safe Email", "csv_row_number": "2"}


def test_should_prepare_phishing_email_sample() -> None:
    sample = prepare_phishing_email_detection_row(
        email_text="Verify your account password at https://example.net/login now.",
        source_id="csv-2",
        original_label="Phishing Email",
        csv_row_number=3,
    )

    assert sample.normalized_label == NORMALIZED_LABEL_SUSPICIOUS
    assert sample.urls == ("https://example.net/login",)


def test_should_build_stable_sample_id_for_same_input() -> None:
    first_sample = prepare_phishing_email_detection_row(
        email_text="Verify your account.",
        source_id="csv-2",
        original_label="Phishing Email",
        csv_row_number=3,
    )
    second_sample = prepare_phishing_email_detection_row(
        email_text="Verify your account.",
        source_id="csv-2",
        original_label="Phishing Email",
        csv_row_number=3,
    )

    assert first_sample.sample_id == second_sample.sample_id
