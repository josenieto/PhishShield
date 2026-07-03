from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


def test_should_decode_utf8_encoded_subject_header() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: =?utf-8?q?Urgent_account_notice?=",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Body.",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.subject == "Urgent account notice"


def test_should_keep_plain_subject_header_unchanged() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Plain subject",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Body.",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.subject == "Plain subject"
