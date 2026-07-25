import pytest

from tools.ml_data_preparation.phishshield_fixtures import (
    NORMALIZED_LABEL_BENIGN,
    NORMALIZED_LABEL_SUSPICIOUS,
    PHISHSHIELD_FIXTURE_SOURCE,
    PHISHSHIELD_FIXTURE_SOURCE_URI,
    prepare_phishshield_fixture_email,
)


def test_should_prepare_benign_phishshield_fixture_sample() -> None:
    sample = prepare_phishshield_fixture_email(
        raw_email=_sample_email_bytes(),
        source_id="benign_sample.eml",
        normalized_label=NORMALIZED_LABEL_BENIGN,
    )

    assert sample.source == PHISHSHIELD_FIXTURE_SOURCE
    assert sample.source_id == "benign_sample.eml"
    assert sample.source_uri == PHISHSHIELD_FIXTURE_SOURCE_URI
    assert sample.original_label == NORMALIZED_LABEL_BENIGN
    assert sample.normalized_label == NORMALIZED_LABEL_BENIGN
    assert sample.subject == "Fixture sample"
    assert sample.body_text == "Please review https://example.com/status."
    assert sample.sender_domain == "example.com"
    assert sample.urls == ("https://example.com/status",)
    assert sample.metadata == {"fixture_name": "benign_sample.eml"}


def test_should_prepare_suspicious_phishshield_fixture_sample() -> None:
    sample = prepare_phishshield_fixture_email(
        raw_email=_sample_email_bytes(),
        source_id="suspicious_sample.eml",
        normalized_label=NORMALIZED_LABEL_SUSPICIOUS,
    )

    assert sample.normalized_label == NORMALIZED_LABEL_SUSPICIOUS


def test_should_reject_unknown_phishshield_fixture_label() -> None:
    with pytest.raises(ValueError, match="Unsupported PhishShield fixture label"):
        prepare_phishshield_fixture_email(
            raw_email=_sample_email_bytes(),
            source_id="unknown_sample.eml",
            normalized_label="unknown",
        )


def test_should_build_stable_sample_id_for_same_fixture_input() -> None:
    first_sample = prepare_phishshield_fixture_email(
        raw_email=_sample_email_bytes(),
        source_id="sample.eml",
        normalized_label=NORMALIZED_LABEL_BENIGN,
    )
    second_sample = prepare_phishshield_fixture_email(
        raw_email=_sample_email_bytes(),
        source_id="sample.eml",
        normalized_label=NORMALIZED_LABEL_BENIGN,
    )

    assert first_sample.sample_id == second_sample.sample_id


def _sample_email_bytes() -> bytes:
    return b"\r\n".join(
        [
            b"From: Fixture Team <fixture@example.com>",
            b"Subject: Fixture sample",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Please review https://example.com/status.",
        ]
    )
