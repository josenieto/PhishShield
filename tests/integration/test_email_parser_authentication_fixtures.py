from pathlib import Path

from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "emails"


def test_should_extract_authentication_results_from_eml_fixture() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (_FIXTURES_DIR / "authentication_results_pass.eml").read_bytes()

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.sender_domain == "example.com"
    assert extracted_email.subject == "Account notice"
    assert extracted_email.body_text == "Please review your account."
    assert extracted_email.spf_result == "pass"
    assert extracted_email.dkim_result == "pass"
    assert extracted_email.dmarc_result == "pass"


def test_should_extract_received_spf_fallback_from_eml_fixture() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (_FIXTURES_DIR / "received_spf_fail.eml").read_bytes()

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.sender_domain == "example.com"
    assert extracted_email.subject == "Account notice"
    assert extracted_email.body_text == "Please review your account."
    assert extracted_email.spf_result == "fail"
    assert extracted_email.dkim_result == "unknown"
    assert extracted_email.dmarc_result == "unknown"
