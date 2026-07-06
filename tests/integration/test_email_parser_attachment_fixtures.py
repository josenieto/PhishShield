from pathlib import Path

from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "emails"


def test_should_extract_attachment_from_multipart_eml_fixture() -> None:
    adapter = PythonEmailContentExtractorAdapter()
    email_bytes = (_FIXTURES_DIR / "multipart_with_attachment.eml").read_bytes()

    extracted_email = adapter.extract(email_bytes)

    assert extracted_email.sender_domain == "example.com"
    assert extracted_email.subject == "Invoice attached"
    assert extracted_email.body_text == "Please review the attached invoice."
    assert extracted_email.attachment_filenames == ("invoice.pdf",)
