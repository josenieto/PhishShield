from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


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
