from domain.services.finding_analysis.finding_definitions import (
    build_finding_from_code,
    build_findings_from_codes,
)
from domain.value_objects.finding import (
    FINDING_CATEGORY_DOMAIN,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_MEDIUM,
    Finding,
)


def test_should_build_known_domain_finding_from_code() -> None:
    assert build_finding_from_code("DOMAIN_CONTAINS_PUNYCODE") == Finding(
        code="DOMAIN_CONTAINS_PUNYCODE",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_build_mixed_script_domain_finding_from_code() -> None:
    assert build_finding_from_code("DOMAIN_HAS_MIXED_SCRIPTS") == Finding(
        code="DOMAIN_HAS_MIXED_SCRIPTS",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_build_confusable_domain_finding_from_code() -> None:
    assert build_finding_from_code("DOMAIN_HAS_CONFUSABLE_CHARACTERS") == Finding(
        code="DOMAIN_HAS_CONFUSABLE_CHARACTERS",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_build_suspicious_domain_depth_finding_from_code() -> None:
    assert build_finding_from_code("DOMAIN_HAS_SUSPICIOUS_DEPTH") == Finding(
        code="DOMAIN_HAS_SUSPICIOUS_DEPTH",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_MEDIUM,
    )


def test_should_build_ip_address_domain_finding_from_code() -> None:
    assert build_finding_from_code("DOMAIN_LOOKS_LIKE_IP_ADDRESS") == Finding(
        code="DOMAIN_LOOKS_LIKE_IP_ADDRESS",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_MEDIUM,
    )


def test_should_build_suspicious_tld_domain_finding_from_code() -> None:
    assert build_finding_from_code("DOMAIN_HAS_SUSPICIOUS_TLD") == Finding(
        code="DOMAIN_HAS_SUSPICIOUS_TLD",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_MEDIUM,
    )


def test_should_build_domain_findings_from_codes_preserving_order() -> None:
    assert build_findings_from_codes(
        [
            "DOMAIN_CONTAINS_PUNYCODE",
            "DOMAIN_HAS_MIXED_SCRIPTS",
            "DOMAIN_HAS_CONFUSABLE_CHARACTERS",
            "DOMAIN_HAS_SUSPICIOUS_DEPTH",
            "DOMAIN_LOOKS_LIKE_IP_ADDRESS",
            "DOMAIN_HAS_SUSPICIOUS_TLD",
        ]
    ) == [
        Finding(
            code="DOMAIN_CONTAINS_PUNYCODE",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_HIGH,
        ),
        Finding(
            code="DOMAIN_HAS_MIXED_SCRIPTS",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_HIGH,
        ),
        Finding(
            code="DOMAIN_HAS_CONFUSABLE_CHARACTERS",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_HIGH,
        ),
        Finding(
            code="DOMAIN_HAS_SUSPICIOUS_DEPTH",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_MEDIUM,
        ),
        Finding(
            code="DOMAIN_LOOKS_LIKE_IP_ADDRESS",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_MEDIUM,
        ),
        Finding(
            code="DOMAIN_HAS_SUSPICIOUS_TLD",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_MEDIUM,
        ),
    ]
