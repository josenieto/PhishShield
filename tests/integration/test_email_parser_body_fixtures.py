from pathlib import Path

from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "emails"


def test_should_extract_visible_text_from_html_only_eml_fixture() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (_FIXTURES_DIR / "html_only_notice.eml").read_bytes()

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.sender_domain == "example.com"
    assert extracted_email.subject == "HTML notice"
    assert extracted_email.body_text == (
        "Account notice Please verify your account at https://example.com/login."
    )
    assert extracted_email.urls == ("https://example.com/login",)
