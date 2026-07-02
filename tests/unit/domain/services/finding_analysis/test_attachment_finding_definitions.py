import pytest

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


@pytest.mark.parametrize(
    ("code", "severity"),
    [
        ("ATTACHMENT_HAS_EXECUTABLE_EXTENSION", FINDING_SEVERITY_CRITICAL),
        ("ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION", FINDING_SEVERITY_MEDIUM),
        ("ATTACHMENT_HAS_DOUBLE_EXTENSION", FINDING_SEVERITY_HIGH),
        ("ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS", FINDING_SEVERITY_HIGH),
    ],
)
def test_should_build_attachment_finding_from_code(code: str, severity: str) -> None:
    assert build_finding_from_code(code) == Finding(
        code=code,
        category=FINDING_CATEGORY_ATTACHMENT,
        severity=severity,
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
