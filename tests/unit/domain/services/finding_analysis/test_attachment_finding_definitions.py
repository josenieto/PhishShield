from domain.services.finding_analysis.finding_definitions import (
    build_finding_from_code,
    build_findings_from_codes,
)
from domain.value_objects.finding import (
    FINDING_CATEGORY_ATTACHMENT,
    FINDING_SEVERITY_CRITICAL,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_MEDIUM,
    Finding,
)


def test_should_build_known_attachment_finding_from_code() -> None:
    assert build_finding_from_code("ATTACHMENT_HAS_EXECUTABLE_EXTENSION") == Finding(
        code="ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
        category=FINDING_CATEGORY_ATTACHMENT,
        severity=FINDING_SEVERITY_CRITICAL,
    )


def test_should_build_office_document_attachment_finding_from_code() -> None:
    assert build_finding_from_code("ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION") == Finding(
        code="ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION",
        category=FINDING_CATEGORY_ATTACHMENT,
        severity=FINDING_SEVERITY_MEDIUM,
    )


def test_should_build_double_extension_attachment_finding_from_code() -> None:
    assert build_finding_from_code("ATTACHMENT_HAS_DOUBLE_EXTENSION") == Finding(
        code="ATTACHMENT_HAS_DOUBLE_EXTENSION",
        category=FINDING_CATEGORY_ATTACHMENT,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_build_suspicious_filename_chars_attachment_finding_from_code() -> None:
    assert build_finding_from_code("ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS") == Finding(
        code="ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS",
        category=FINDING_CATEGORY_ATTACHMENT,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_build_attachment_findings_from_codes_preserving_order() -> None:
    assert build_findings_from_codes(
        [
            "ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
            "ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION",
            "ATTACHMENT_HAS_DOUBLE_EXTENSION",
            "ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS",
        ]
    ) == [
        Finding(
            code="ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
            category=FINDING_CATEGORY_ATTACHMENT,
            severity=FINDING_SEVERITY_CRITICAL,
        ),
        Finding(
            code="ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION",
            category=FINDING_CATEGORY_ATTACHMENT,
            severity=FINDING_SEVERITY_MEDIUM,
        ),
        Finding(
            code="ATTACHMENT_HAS_DOUBLE_EXTENSION",
            category=FINDING_CATEGORY_ATTACHMENT,
            severity=FINDING_SEVERITY_HIGH,
        ),
        Finding(
            code="ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS",
            category=FINDING_CATEGORY_ATTACHMENT,
            severity=FINDING_SEVERITY_HIGH,
        ),
    ]
