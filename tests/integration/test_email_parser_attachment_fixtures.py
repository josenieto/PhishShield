from pathlib import Path

from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "emails"


def test_should_extract_attachment_from_multipart_eml_fixture() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (_FIXTURES_DIR / "multipart_with_attachment.eml").read_bytes()

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.sender_domain == "example.com"
    assert extracted_email.subject == "Invoice attached"
    assert extracted_email.body_text == "Please review the attached invoice."
    assert extracted_email.attachment_filenames == ("invoice.pdf",)


def test_should_extract_encoded_subject_and_attachment_from_eml_fixture() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (_FIXTURES_DIR / "encoded_subject_and_attachment.eml").read_bytes()

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.sender_domain == "example.com"
    assert extracted_email.subject == "Urgent invoice notice"
    assert extracted_email.body_text == "Please review the attached invoice."
    assert extracted_email.attachment_filenames == ("invoice.pdf",)


def test_should_extract_multiple_attachments_from_multipart_eml_fixture() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (_FIXTURES_DIR / "multipart_with_multiple_attachments.eml").read_bytes()

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.sender_domain == "example.com"
    assert extracted_email.subject == "Multiple attachments"
    assert extracted_email.body_text == "Please review the attached documents."
    assert extracted_email.attachment_filenames == (
        "invoice.pdf",
        "payment-details.zip",
        "notes.txt",
    )


def test_should_extract_body_and_attachment_from_nested_multipart_eml_fixture() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (_FIXTURES_DIR / "nested_multipart_with_attachment.eml").read_bytes()

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.sender_domain == "example.com"
    assert extracted_email.subject == "Nested multipart"
    assert extracted_email.body_text == "Please review your account summary."
    assert extracted_email.attachment_filenames == ("summary.pdf",)
    assert extracted_email.spf_result == "pass"
    assert extracted_email.dkim_result == "pass"
    assert extracted_email.dmarc_result == "pass"


def test_should_preserve_plain_body_html_link_and_attachment_in_nested_multipart_fixture() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (
        _FIXTURES_DIR / "nested_multipart_with_html_link_and_attachment.eml"
    ).read_bytes()

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.sender_domain == "example.com"
    assert extracted_email.subject == "Nested account notice"
    assert extracted_email.body_text == "Please review your account at https://example.com/plain."
    assert extracted_email.urls == (
        "https://example.com/plain",
        "https://example.com/html",
    )
    assert extracted_email.attachment_filenames == ("account-summary.pdf",)
    assert extracted_email.spf_result == "pass"
    assert extracted_email.dkim_result == "pass"
    assert extracted_email.dmarc_result == "pass"


def test_should_exclude_inline_logo_but_keep_real_attachment_from_related_fixture() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (_FIXTURES_DIR / "inline_logo_with_real_attachment.eml").read_bytes()

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.body_text == (
        "Please review your invoice at https://example.com/invoice."
    )
    assert extracted_email.urls == ("https://example.com/invoice",)
    assert extracted_email.attachment_filenames == ("invoice.pdf",)


def test_should_fallback_to_visible_html_when_nested_plain_body_is_empty() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (
        _FIXTURES_DIR / "multipart_empty_plain_html_link_inline_attachment.eml"
    ).read_bytes()

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.body_text == "Please review your invoice. Open invoice"
    assert extracted_email.urls == ("https://example.com/invoice",)
    assert extracted_email.attachment_filenames == ("invoice.pdf",)
    assert extracted_email.spf_result == "pass"
    assert extracted_email.dkim_result == "pass"
    assert extracted_email.dmarc_result == "pass"
