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


def is_executable_extension(filename: str) -> bool:
    """Return True when a filename ends with an executable extension."""
    normalized_filename = filename.strip().lower()

    return any(
        normalized_filename.endswith(extension)
        for extension in EXECUTABLE_EXTENSIONS
    )
