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


def test_should_decode_latin1_plain_text_body_from_eml_fixture() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (_FIXTURES_DIR / "latin1_body_notice.eml").read_bytes().replace(
        b"__LATIN1_BODY__",
        "Revisión de cuenta requerida.".encode("iso-8859-1"),
    )

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.sender_domain == "example.com"
    assert extracted_email.subject == "Account notice"
    assert extracted_email.body_text == "Revisión de cuenta requerida."


def test_should_decode_quoted_printable_plain_text_body_from_eml_fixture() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (_FIXTURES_DIR / "quoted_printable_body_notice.eml").read_bytes()

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.sender_domain == "example.com"
    assert extracted_email.subject == "Account notice"
    assert extracted_email.body_text == "Please review your account summary."
