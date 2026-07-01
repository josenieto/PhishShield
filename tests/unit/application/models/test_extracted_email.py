from dataclasses import FrozenInstanceError

import pytest

from application.models.extracted_email import ExtractedEmailContent


def test_should_store_extracted_email_content() -> None:
    extracted_email = ExtractedEmailContent(
        sender_domain="example.com",
        urls=("https://example.com/login",),
        attachment_filenames=("invoice.pdf",),
        subject="Invoice available",
        body_text="Please review the attached invoice.",
        spf_result="pass",
        dkim_result="pass",
        dmarc_result="pass",
    )

    assert extracted_email.sender_domain == "example.com"
    assert extracted_email.urls == ("https://example.com/login",)
    assert extracted_email.attachment_filenames == ("invoice.pdf",)
    assert extracted_email.subject == "Invoice available"
    assert extracted_email.body_text == "Please review the attached invoice."
    assert extracted_email.spf_result == "pass"
    assert extracted_email.dkim_result == "pass"
    assert extracted_email.dmarc_result == "pass"


def test_should_support_empty_extracted_email_collections() -> None:
    extracted_email = ExtractedEmailContent(
        sender_domain="example.com",
        urls=(),
        attachment_filenames=(),
        subject="",
        body_text="",
        spf_result="unknown",
        dkim_result="unknown",
        dmarc_result="unknown",
    )

    assert extracted_email.urls == ()
    assert extracted_email.attachment_filenames == ()


def test_should_compare_extracted_email_content_by_value() -> None:
    first_email = ExtractedEmailContent(
        sender_domain="example.com",
        urls=("https://example.com",),
        attachment_filenames=("invoice.pdf",),
        subject="Subject",
        body_text="Body",
        spf_result="pass",
        dkim_result="pass",
        dmarc_result="pass",
    )
    second_email = ExtractedEmailContent(
        sender_domain="example.com",
        urls=("https://example.com",),
        attachment_filenames=("invoice.pdf",),
        subject="Subject",
        body_text="Body",
        spf_result="pass",
        dkim_result="pass",
        dmarc_result="pass",
    )

    assert first_email == second_email


def test_should_keep_different_extracted_email_content_distinct() -> None:
    first_email = ExtractedEmailContent(
        sender_domain="example.com",
        urls=("https://example.com",),
        attachment_filenames=(),
        subject="Subject",
        body_text="Body",
        spf_result="pass",
        dkim_result="pass",
        dmarc_result="pass",
    )
    second_email = ExtractedEmailContent(
        sender_domain="example.org",
        urls=("https://example.org",),
        attachment_filenames=(),
        subject="Subject",
        body_text="Body",
        spf_result="pass",
        dkim_result="pass",
        dmarc_result="pass",
    )

    assert first_email != second_email


def test_should_be_immutable() -> None:
    extracted_email = ExtractedEmailContent(
        sender_domain="example.com",
        urls=(),
        attachment_filenames=(),
        subject="Subject",
        body_text="Body",
        spf_result="pass",
        dkim_result="pass",
        dmarc_result="pass",
    )

    with pytest.raises(FrozenInstanceError):
        extracted_email.sender_domain = "example.org"
