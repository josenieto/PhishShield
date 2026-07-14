from domain.services.finding_analysis.finding_definitions import (
    build_finding_from_code,
    build_findings_from_codes,
)
from domain.value_objects.finding import (
    FINDING_CATEGORY_AUTHENTICATION,
    FINDING_CATEGORY_DOMAIN,
    FINDING_CATEGORY_UNKNOWN,
    FINDING_CATEGORY_URL,
    FINDING_SEVERITY_CRITICAL,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_UNKNOWN,
    Finding,
)


def test_should_build_unknown_finding_from_unmapped_code() -> None:
    assert build_finding_from_code("UNKNOWN_FINDING_CODE") == Finding(
        code="UNKNOWN_FINDING_CODE",
        category=FINDING_CATEGORY_UNKNOWN,
        severity=FINDING_SEVERITY_UNKNOWN,
        explanation="No explanation is available for this finding code yet.",
    )


def test_should_build_findings_from_codes_preserving_order() -> None:
    assert build_findings_from_codes(
        [
            "DOMAIN_CONTAINS_PUNYCODE",
            "URL_HAS_EMBEDDED_CREDENTIALS",
            "AUTHENTICATION_DMARC_FAILED",
        ]
    ) == [
        Finding(
            code="DOMAIN_CONTAINS_PUNYCODE",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_HIGH,
            explanation="The domain contains Punycode, which can be used to create visually deceptive lookalike domains.",
        ),
        Finding(
            code="URL_HAS_EMBEDDED_CREDENTIALS",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_HIGH,
            explanation="The URL includes embedded credentials, which can hide the real destination and mislead the user.",
        ),
        Finding(
            code="AUTHENTICATION_DMARC_FAILED",
            category=FINDING_CATEGORY_AUTHENTICATION,
            severity=FINDING_SEVERITY_CRITICAL,
            explanation="DMARC authentication failed, which can indicate that the message does not align with the claimed sender domain policy.",
        ),
    ]


def test_should_build_findings_from_codes_preserving_duplicates() -> None:
    assert build_findings_from_codes(
        [
            "DOMAIN_CONTAINS_PUNYCODE",
            "DOMAIN_CONTAINS_PUNYCODE",
        ]
    ) == [
        Finding(
            code="DOMAIN_CONTAINS_PUNYCODE",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_HIGH,
            explanation="The domain contains Punycode, which can be used to create visually deceptive lookalike domains.",
        ),
        Finding(
            code="DOMAIN_CONTAINS_PUNYCODE",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_HIGH,
            explanation="The domain contains Punycode, which can be used to create visually deceptive lookalike domains.",
        ),
    ]


def test_should_return_empty_list_when_building_findings_from_empty_codes() -> None:
    assert build_findings_from_codes([]) == []
