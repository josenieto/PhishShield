from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


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


def test_should_decode_encoded_attachment_filename() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Encoded attachment",
            b"Content-Type: multipart/mixed; boundary=boundary",
            b"",
            b"--boundary",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"See attachment.",
            b"--boundary",
            b"Content-Type: application/pdf",
            b"Content-Disposition: attachment; filename=\"=?utf-8?b?aW52b2ljZS5wZGY=?=\"",
            b"",
            b"fake pdf bytes",
            b"--boundary--",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.attachment_filenames == ("invoice.pdf",)
