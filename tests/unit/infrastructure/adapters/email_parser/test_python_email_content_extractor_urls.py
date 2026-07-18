from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


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


def test_should_extract_urls_from_html_only_body() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: HTML link",
            b"Content-Type: text/html; charset=utf-8",
            b"",
            b"<html><body>Please visit https://example.com/login.</body></html>",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.urls == ("https://example.com/login",)


def test_should_extract_urls_from_html_anchor_href() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: HTML anchor",
            b"Content-Type: text/html; charset=utf-8",
            b"",
            b"<html><body><a href=\"https://example.com/login\">Verify account</a></body></html>",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.body_text == "Verify account"
    assert extracted_email.urls == ("https://example.com/login",)


def test_should_deduplicate_visible_and_href_urls_in_html_only_body() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: HTML links",
            b"Content-Type: text/html; charset=utf-8",
            b"",
            b"<html><body>Visit https://example.com/login <a href=\"https://example.com/login\">now</a></body></html>",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.urls == ("https://example.com/login",)


def test_should_not_extract_urls_after_body_size_limit() -> None:
    adapter = PythonEmailContentExtractorAdapter(max_body_chars=20)
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Limited links",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"This prefix is long. https://example.com/login",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.body_text == "This prefix is long."
    assert extracted_email.urls == ()


def test_should_extract_urls_before_body_size_limit() -> None:
    adapter = PythonEmailContentExtractorAdapter(max_body_chars=31)
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@example.com>",
            b"Subject: Limited links",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"https://example.com/login after limit",
        ]
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.body_text == "https://example.com/login after"
    assert extracted_email.urls == ("https://example.com/login",)
