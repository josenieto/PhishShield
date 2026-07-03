from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


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


def test_should_extract_visible_text_from_html_only_email() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: HTML",
            b"Content-Type: text/html; charset=utf-8",
            b"",
            b"<html><body><p>Urgent account notice</p><p>Review now</p></body></html>",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.body_text == "Urgent account notice Review now"


def test_should_decode_html_entities_in_html_only_email() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: HTML",
            b"Content-Type: text/html; charset=utf-8",
            b"",
            b"<html><body>Payment&nbsp;required &amp; urgent</body></html>",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.body_text == "Payment required & urgent"


def test_should_prefer_plain_text_over_html_when_both_are_available() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Alternative",
            b"Content-Type: multipart/alternative; boundary=boundary",
            b"",
            b"--boundary",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Plain body.",
            b"--boundary",
            b"Content-Type: text/html; charset=utf-8",
            b"",
            b"<html><body>HTML body.</body></html>",
            b"--boundary--",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.body_text == "Plain body."


def test_should_ignore_html_attachment_as_body_text() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: HTML attachment",
            b"Content-Type: multipart/mixed; boundary=boundary",
            b"",
            b"--boundary",
            b"Content-Type: text/html; charset=utf-8",
            b"Content-Disposition: attachment; filename=\"message.html\"",
            b"",
            b"<html><body>Attached HTML should not be body.</body></html>",
            b"--boundary--",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.body_text == ""
