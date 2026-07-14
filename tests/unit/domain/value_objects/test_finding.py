from dataclasses import FrozenInstanceError

import pytest

from domain.value_objects.finding import (
    FINDING_CATEGORY_ATTACHMENT,
    FINDING_CATEGORY_AUTHENTICATION,
    FINDING_CATEGORY_DOMAIN,
    FINDING_CATEGORY_RISK,
    FINDING_CATEGORY_SOCIAL_ENGINEERING,
    FINDING_CATEGORY_UNKNOWN,
    FINDING_CATEGORY_URL,
    FINDING_SEVERITY_CRITICAL,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_LOW,
    FINDING_SEVERITY_MEDIUM,
    FINDING_SEVERITY_UNKNOWN,
    Finding,
)


def test_should_store_finding_values() -> None:
    finding = Finding(
        code="URL_HAS_EMBEDDED_CREDENTIALS",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_HIGH,
        explanation="The URL includes embedded credentials.",
    )

    assert finding.code == "URL_HAS_EMBEDDED_CREDENTIALS"
    assert finding.category == FINDING_CATEGORY_URL
    assert finding.severity == FINDING_SEVERITY_HIGH
    assert finding.explanation == "The URL includes embedded credentials."


def test_should_compare_findings_by_value() -> None:
    assert Finding("A_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH) == Finding(
        "A_FINDING",
        FINDING_CATEGORY_URL,
        FINDING_SEVERITY_HIGH,
    )


def test_should_keep_different_findings_distinct() -> None:
    assert Finding("A_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH) != Finding(
        "B_FINDING",
        FINDING_CATEGORY_URL,
        FINDING_SEVERITY_HIGH,
    )


def test_should_default_explanation_to_empty_string() -> None:
    finding = Finding("A_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH)

    assert finding.explanation == ""


def test_should_be_immutable() -> None:
    finding = Finding("A_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH)

    with pytest.raises(FrozenInstanceError):
        finding.code = "B_FINDING"


def test_should_expose_finding_category_constants() -> None:
    assert FINDING_CATEGORY_DOMAIN == "DOMAIN"
    assert FINDING_CATEGORY_URL == "URL"
    assert FINDING_CATEGORY_ATTACHMENT == "ATTACHMENT"
    assert FINDING_CATEGORY_AUTHENTICATION == "AUTHENTICATION"
    assert FINDING_CATEGORY_SOCIAL_ENGINEERING == "SOCIAL_ENGINEERING"
    assert FINDING_CATEGORY_RISK == "RISK"
    assert FINDING_CATEGORY_UNKNOWN == "UNKNOWN"


def test_should_expose_finding_severity_constants() -> None:
    assert FINDING_SEVERITY_LOW == "LOW"
    assert FINDING_SEVERITY_MEDIUM == "MEDIUM"
    assert FINDING_SEVERITY_HIGH == "HIGH"
    assert FINDING_SEVERITY_CRITICAL == "CRITICAL"
    assert FINDING_SEVERITY_UNKNOWN == "UNKNOWN"
