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


def test_should_extract_https_url_from_plain_text_body() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Link",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Please visit https://example.com/login",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.urls == ("https://example.com/login",)


def test_should_extract_http_url_from_plain_text_body() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Link",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Please visit http://example.com/login",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.urls == ("http://example.com/login",)


def test_should_extract_multiple_urls_preserving_order() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Links",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"First https://first.example/login then http://second.example/reset",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.urls == (
        "https://first.example/login",
        "http://second.example/reset",
    )


def test_should_strip_trailing_url_punctuation() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Link",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Open (https://example.com/login).",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.urls == ("https://example.com/login",)


def test_should_preserve_duplicate_urls() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Links",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"https://example.com https://example.com",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.urls == (
        "https://example.com",
        "https://example.com",
    )


def test_should_ignore_non_http_urls() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Link",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"javascript:alert(1) mailto:user@example.com data:text/plain,test",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.urls == ()


def test_should_extract_urls_from_multipart_plain_text_body() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Multipart links",
            b"Content-Type: multipart/mixed; boundary=boundary",
            b"",
            b"--boundary",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"First https://first.example/login",
            b"--boundary",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Second http://second.example/reset",
            b"--boundary--",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.urls == (
        "https://first.example/login",
        "http://second.example/reset",
    )


def test_should_return_empty_urls_when_plain_text_body_has_no_urls() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: No links",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"There are no links here.",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.urls == ()


def test_should_extract_pass_authentication_results_from_headers() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Auth",
            b"Authentication-Results: mx.example.com; spf=pass smtp.mailfrom=example.com; dkim=pass header.d=example.com; dmarc=pass header.from=example.com",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Body.",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.spf_result == "pass"
    assert extracted_email.dkim_result == "pass"
    assert extracted_email.dmarc_result == "pass"


def test_should_extract_fail_authentication_results_from_headers() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Auth",
            b"Authentication-Results: mx.example.com; spf=fail smtp.mailfrom=bad.example; dkim=fail header.d=bad.example; dmarc=fail header.from=bad.example",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Body.",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.spf_result == "fail"
    assert extracted_email.dkim_result == "fail"
    assert extracted_email.dmarc_result == "fail"


def test_should_keep_unknown_authentication_results_when_header_is_missing() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: No auth",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Body.",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.spf_result == "unknown"
    assert extracted_email.dkim_result == "unknown"
    assert extracted_email.dmarc_result == "unknown"


def test_should_keep_unknown_for_missing_individual_authentication_results() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Partial auth",
            b"Authentication-Results: mx.example.com; spf=pass smtp.mailfrom=example.com",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Body.",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.spf_result == "pass"
    assert extracted_email.dkim_result == "unknown"
    assert extracted_email.dmarc_result == "unknown"


def test_should_extract_authentication_results_case_insensitively() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Auth",
            b"Authentication-Results: mx.example.com; SPF=PASS smtp.mailfrom=example.com; DKIM=FAIL header.d=bad.example; DMARC=PASS header.from=example.com",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Body.",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.spf_result == "pass"
    assert extracted_email.dkim_result == "fail"
    assert extracted_email.dmarc_result == "pass"
