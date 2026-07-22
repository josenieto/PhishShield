from types import MappingProxyType

import pytest

from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample
from tools.ml_data_preparation.spamassassin import (
    NORMALIZED_LABEL_BENIGN,
    NORMALIZED_LABEL_SUSPICIOUS,
    SPAMASSASSIN_SOURCE,
    SPAMASSASSIN_SOURCE_URI,
    normalize_spamassassin_label,
    prepare_spamassassin_email,
)


def test_should_normalize_ham_labels_as_benign() -> None:
    assert normalize_spamassassin_label("easy_ham") == NORMALIZED_LABEL_BENIGN
    assert normalize_spamassassin_label("hard_ham") == NORMALIZED_LABEL_BENIGN
    assert normalize_spamassassin_label("ham") == NORMALIZED_LABEL_BENIGN


def test_should_normalize_spam_label_as_suspicious() -> None:
    assert normalize_spamassassin_label("spam") == NORMALIZED_LABEL_SUSPICIOUS


def test_should_reject_unknown_spamassassin_label() -> None:
    with pytest.raises(ValueError, match="Unsupported SpamAssassin label"):
        normalize_spamassassin_label("phishing")


def test_should_prepare_spamassassin_email_sample_from_raw_email() -> None:
    sample = prepare_spamassassin_email(
        raw_email=_sample_email_bytes(),
        source_id="easy-ham-0001",
        original_label="easy_ham",
    )

    assert sample.source == SPAMASSASSIN_SOURCE
    assert sample.source_id == "easy-ham-0001"
    assert sample.source_uri == SPAMASSASSIN_SOURCE_URI
    assert sample.original_label == "easy_ham"
    assert sample.normalized_label == NORMALIZED_LABEL_BENIGN
    assert sample.subject == "Weekly account summary"
    assert sample.body_text == "Please review your account summary at https://example.com/summary."
    assert sample.sender_domain == "example.com"
    assert sample.urls == ("https://example.com/summary",)
    assert sample.attachment_filenames == ()
    assert sample.raw_available is True
    assert sample.metadata == {"original_label": "easy_ham"}


def test_should_build_stable_sample_id_for_same_input() -> None:
    first_sample = prepare_spamassassin_email(
        raw_email=_sample_email_bytes(),
        source_id="easy-ham-0001",
        original_label="easy_ham",
    )
    second_sample = prepare_spamassassin_email(
        raw_email=_sample_email_bytes(),
        source_id="easy-ham-0001",
        original_label="easy_ham",
    )

    assert first_sample.sample_id == second_sample.sample_id


def test_should_change_sample_id_when_source_id_changes() -> None:
    first_sample = prepare_spamassassin_email(
        raw_email=_sample_email_bytes(),
        source_id="easy-ham-0001",
        original_label="easy_ham",
    )
    second_sample = prepare_spamassassin_email(
        raw_email=_sample_email_bytes(),
        source_id="easy-ham-0002",
        original_label="easy_ham",
    )

    assert first_sample.sample_id != second_sample.sample_id


def test_should_convert_collection_fields_to_immutable_shapes() -> None:
    sample = PreparedEmailSample(
        sample_id="sample-id",
        source="spamassassin",
        source_id="message-id",
        source_uri="https://example.com/source",
        original_label="spam",
        normalized_label="suspicious",
        subject="Subject",
        body_text="Body",
        sender_domain="example.com",
        urls=["https://example.com"],
        attachment_filenames=["invoice.pdf"],
        raw_available=True,
        metadata={"original_label": "spam"},
    )

    assert sample.urls == ("https://example.com",)
    assert sample.attachment_filenames == ("invoice.pdf",)
    assert isinstance(sample.metadata, MappingProxyType)


def _sample_email_bytes() -> bytes:
    return b"\r\n".join(
        [
            b"From: Product Team <updates@example.com>",
            b"Subject: Weekly account summary",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Please review your account summary at https://example.com/summary.",
        ]
    )
