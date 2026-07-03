from application.models.extracted_email import ExtractedEmailContent
from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


def test_should_extract_basic_plain_text_email_content() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Hello",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"This is the body.",
        ]
    )

    assert adapter.extract(email_bytes) == ExtractedEmailContent(
        sender_domain="example.com",
        urls=(),
        attachment_filenames=(),
        subject="Hello",
        body_text="This is the body.",
        spf_result="unknown",
        dkim_result="unknown",
        dmarc_result="unknown",
    )


def test_should_return_empty_subject_and_sender_domain_when_headers_are_missing() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Body without sender or subject.",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.sender_domain == ""
    assert extracted_email.subject == ""
    assert extracted_email.body_text == "Body without sender or subject."
