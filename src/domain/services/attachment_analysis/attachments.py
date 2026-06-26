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


def _has_extension(filename: str, extensions: frozenset[str]) -> bool:
    normalized_filename = filename.strip().lower()

    return any(
        normalized_filename.endswith(extension)
        for extension in extensions
    )
