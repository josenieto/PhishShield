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


def test_should_extract_plain_text_body_from_multipart_email() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Multipart",
            b"Content-Type: multipart/mixed; boundary=boundary",
            b"",
            b"--boundary",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"First body part.",
            b"--boundary",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Second body part.",
            b"--boundary--",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.body_text == "First body part.\nSecond body part."


def test_should_extract_attachment_filenames() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Attachment",
            b"Content-Type: multipart/mixed; boundary=boundary",
            b"",
            b"--boundary",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"See attachment.",
            b"--boundary",
            b"Content-Type: application/pdf",
            b"Content-Disposition: attachment; filename=\"invoice.pdf\"",
            b"",
            b"fake pdf bytes",
            b"--boundary--",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.attachment_filenames == ("invoice.pdf",)


def test_should_ignore_text_attachment_as_body_text() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Text attachment",
            b"Content-Type: multipart/mixed; boundary=boundary",
            b"",
            b"--boundary",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Real body.",
            b"--boundary",
            b"Content-Type: text/plain; charset=utf-8",
            b"Content-Disposition: attachment; filename=\"notes.txt\"",
            b"",
            b"Attached text should not be body.",
            b"--boundary--",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.body_text == "Real body."
    assert extracted_email.attachment_filenames == ("notes.txt",)
