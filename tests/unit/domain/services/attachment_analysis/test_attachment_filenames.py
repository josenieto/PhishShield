import pytest

from domain.services.attachment_analysis.attachments import (
    has_suspicious_filename_chars,
)


@pytest.mark.parametrize(
    "filename",
    [
        "invoice\u200b.pdf",
        "invоice.pdf",
        "invoiceΑ.pdf",
    ],
)
def test_should_detect_suspicious_attachment_filename_characters(
    filename: str,
) -> None:
    assert has_suspicious_filename_chars(filename) is True


@pytest.mark.parametrize(
    "filename",
    [
        "invoice.pdf",
        "",
        "   ",
    ],
)
def test_should_return_false_when_attachment_filename_has_no_suspicious_characters(
    filename: str,
) -> None:
    assert has_suspicious_filename_chars(filename) is False
