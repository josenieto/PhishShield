import pytest

from domain.services.attachment_analysis.attachments import (
    ATTACHMENT_ARCHIVE,
    ATTACHMENT_EXECUTABLE,
    ATTACHMENT_IMAGE,
    ATTACHMENT_OFFICE,
    ATTACHMENT_PDF,
    ATTACHMENT_TEXT,
    ATTACHMENT_UNKNOWN,
    classify_attachment_extension,
    has_double_extension,
    is_executable_extension,
    is_office_document_extension,
    is_pdf_extension,
)


@pytest.mark.parametrize(
    "filename",
    [
        "invoice.exe",
        "run.BAT",
        "script.ps1",
        "payload.scr",
        "installer.cmd",
        "macro.vbs",
        "dropper.js",
        "archive.jar",
        "invoice.pdf.exe",
    ],
)
def test_should_detect_executable_attachment_extension(filename: str) -> None:
    assert is_executable_extension(filename) is True


@pytest.mark.parametrize(
    "filename",
    [
        "document.pdf",
        "image.png",
        "archive.zip",
        "filename-without-extension",
        "",
        "   ",
    ],
)
def test_should_return_false_when_attachment_extension_is_not_executable(
    filename: str,
) -> None:
    assert is_executable_extension(filename) is False


@pytest.mark.parametrize(
    "filename",
    [
        "report.doc",
        "report.docx",
        "report.docm",
        "sheet.xls",
        "sheet.xlsx",
        "sheet.xlsm",
        "slides.ppt",
        "slides.pptx",
        "slides.pptm",
        "REPORT.DOCM",
    ],
)
def test_should_detect_office_document_attachment_extension(filename: str) -> None:
    assert is_office_document_extension(filename) is True


@pytest.mark.parametrize(
    "filename",
    [
        "document.pdf",
        "image.png",
        "archive.zip",
        "filename-without-extension",
        "",
        "   ",
    ],
)
def test_should_return_false_when_attachment_extension_is_not_office_document(
    filename: str,
) -> None:
    assert is_office_document_extension(filename) is False


@pytest.mark.parametrize(
    "filename",
    [
        "invoice.pdf",
        "INVOICE.PDF",
        " report.pdf ",
    ],
)
def test_should_detect_pdf_attachment_extension(filename: str) -> None:
    assert is_pdf_extension(filename) is True


@pytest.mark.parametrize(
    "filename",
    [
        "invoice.pdf.exe",
        "document.docx",
        "filename-without-extension",
        "",
        "   ",
    ],
)
def test_should_return_false_when_attachment_extension_is_not_pdf(
    filename: str,
) -> None:
    assert is_pdf_extension(filename) is False


@pytest.mark.parametrize(
    "filename",
    [
        "invoice.pdf.exe",
        "document.docx.scr",
        "archive.tar.gz",
        "ARCHIVE.TAR.GZ",
    ],
)
def test_should_detect_double_attachment_extension(filename: str) -> None:
    assert has_double_extension(filename) is True


@pytest.mark.parametrize(
    "filename",
    [
        "invoice.pdf",
        "filename-without-extension",
        ".hiddenfile",
        "",
        "   ",
    ],
)
def test_should_return_false_when_attachment_has_no_double_extension(
    filename: str,
) -> None:
    assert has_double_extension(filename) is False


@pytest.mark.parametrize(
    ("filename", "expected_category"),
    [
        ("invoice.pdf", ATTACHMENT_PDF),
        ("document.docm", ATTACHMENT_OFFICE),
        ("spreadsheet.xlsm", ATTACHMENT_OFFICE),
        ("payload.exe", ATTACHMENT_EXECUTABLE),
        ("photo.png", ATTACHMENT_IMAGE),
        ("archive.zip", ATTACHMENT_ARCHIVE),
        ("notes.txt", ATTACHMENT_TEXT),
        ("README.MD", ATTACHMENT_TEXT),
        ("unknown.bin", ATTACHMENT_UNKNOWN),
        ("filename-without-extension", ATTACHMENT_UNKNOWN),
        ("", ATTACHMENT_UNKNOWN),
        ("   ", ATTACHMENT_UNKNOWN),
    ],
)
def test_should_classify_attachment_extension(
    filename: str,
    expected_category: str,
) -> None:
    assert classify_attachment_extension(filename) == expected_category
