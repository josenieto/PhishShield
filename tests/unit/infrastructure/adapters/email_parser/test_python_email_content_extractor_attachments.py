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


def test_should_ignore_inline_image_with_content_id_as_attachment() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Inline logo",
            b"Content-Type: multipart/related; boundary=boundary",
            b"",
            b"--boundary",
            b"Content-Type: text/html; charset=utf-8",
            b"",
            b"<html><body><img src=\"cid:logo@example.com\"></body></html>",
            b"--boundary",
            b"Content-Type: image/png",
            b"Content-Disposition: inline; filename=\"logo.png\"",
            b"Content-ID: <logo@example.com>",
            b"",
            b"image bytes",
            b"--boundary",
            b"Content-Type: application/pdf",
            b"Content-Disposition: attachment; filename=\"invoice.pdf\"",
            b"",
            b"pdf bytes",
            b"--boundary--",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.attachment_filenames == ("invoice.pdf",)


def test_should_preserve_inline_file_without_content_id_as_attachment() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Inline document",
            b"Content-Type: multipart/mixed; boundary=boundary",
            b"",
            b"--boundary",
            b"Content-Type: application/pdf",
            b"Content-Disposition: inline; filename=\"invoice.pdf\"",
            b"",
            b"pdf bytes",
            b"--boundary--",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.attachment_filenames == ("invoice.pdf",)
