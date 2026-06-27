from domain.services.homoglyphs.confusables import contains_confusable_characters
from domain.services.homoglyphs.scripts import contains_mixed_scripts
from domain.services.text_normalization.invisible_characters import (
    contains_invisible_chars,
)


EXECUTABLE_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".exe",
        ".bat",
        ".cmd",
        ".scr",
        ".ps1",
        ".vbs",
        ".js",
        ".jar",
    }
)

OFFICE_DOCUMENT_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".doc",
        ".docx",
        ".docm",
        ".xls",
        ".xlsx",
        ".xlsm",
        ".ppt",
        ".pptx",
        ".pptm",
    }
)

PDF_EXTENSIONS: frozenset[str] = frozenset({".pdf"})


def is_executable_extension(filename: str) -> bool:
    """Return True when a filename ends with an executable extension."""
    return _has_extension(filename, EXECUTABLE_EXTENSIONS)


def is_office_document_extension(filename: str) -> bool:
    """Return True when a filename ends with an Office document extension."""
    return _has_extension(filename, OFFICE_DOCUMENT_EXTENSIONS)


def is_pdf_extension(filename: str) -> bool:
    """Return True when a filename ends with a PDF extension."""
    return _has_extension(filename, PDF_EXTENSIONS)


def has_double_extension(filename: str) -> bool:
    """Return True when a filename has at least two extension segments."""
    normalized_filename = filename.strip()

    if not normalized_filename or normalized_filename.startswith("."):
        return False

    filename_parts = [
        part
        for part in normalized_filename.split(".")
        if part
    ]

    return len(filename_parts) >= 3


def has_suspicious_filename_chars(filename: str) -> bool:
    """Return True when a filename contains suspicious Unicode characters."""
    return (
        contains_invisible_chars(filename)
        or contains_mixed_scripts(filename)
        or contains_confusable_characters(filename)
    )


def _has_extension(filename: str, extensions: frozenset[str]) -> bool:
    normalized_filename = filename.strip().lower()

    return any(
        normalized_filename.endswith(extension)
        for extension in extensions
    )
