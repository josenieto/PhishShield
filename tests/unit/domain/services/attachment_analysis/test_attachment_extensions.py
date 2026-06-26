import pytest

from domain.services.attachment_analysis.attachments import is_executable_extension


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
