from pathlib import Path

from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "emails"


def test_should_degrade_safely_for_malformed_eml_fixture() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (_FIXTURES_DIR / "malformed_missing_headers.eml").read_bytes()

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.sender_domain == ""
    assert extracted_email.subject == ""
    assert extracted_email.body_text == (
        "This is not a normal RFC822 email.\n"
        "It has no From, no Subject, and no Content-Type.\n"
        "https://example.com/login"
    )
    assert extracted_email.urls == ("https://example.com/login",)
    assert extracted_email.attachment_filenames == ()
    assert extracted_email.spf_result == "unknown"
    assert extracted_email.dkim_result == "unknown"
    assert extracted_email.dmarc_result == "unknown"
