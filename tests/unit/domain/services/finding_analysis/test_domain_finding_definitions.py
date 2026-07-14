import pytest

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


@pytest.mark.parametrize(
    ("code", "severity"),
    [
        ("DOMAIN_CONTAINS_PUNYCODE", FINDING_SEVERITY_HIGH),
        ("DOMAIN_HAS_MIXED_SCRIPTS", FINDING_SEVERITY_HIGH),
        ("DOMAIN_HAS_CONFUSABLE_CHARACTERS", FINDING_SEVERITY_HIGH),
        ("DOMAIN_HAS_SUSPICIOUS_DEPTH", FINDING_SEVERITY_MEDIUM),
        ("DOMAIN_LOOKS_LIKE_IP_ADDRESS", FINDING_SEVERITY_MEDIUM),
        ("DOMAIN_HAS_SUSPICIOUS_TLD", FINDING_SEVERITY_MEDIUM),
    ],
)
def test_should_build_domain_finding_from_code(code: str, severity: str) -> None:
    finding = build_finding_from_code(code)

    assert finding == Finding(
        code=code,
        category=FINDING_CATEGORY_DOMAIN,
        severity=severity,
        explanation=finding.explanation,
    )
    assert finding.explanation != ""


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
            explanation="The domain contains Punycode, which can be used to create visually deceptive lookalike domains.",
        ),
        Finding(
            code="DOMAIN_HAS_MIXED_SCRIPTS",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_HIGH,
            explanation="The domain mixes characters from multiple writing systems, which can indicate an impersonation attempt.",
        ),
        Finding(
            code="DOMAIN_HAS_CONFUSABLE_CHARACTERS",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_HIGH,
            explanation="The domain contains characters that can visually imitate trusted brand names or domains.",
        ),
        Finding(
            code="DOMAIN_HAS_SUSPICIOUS_DEPTH",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_MEDIUM,
            explanation="The domain has an unusually deep subdomain structure, which can be used to disguise the true host.",
        ),
        Finding(
            code="DOMAIN_LOOKS_LIKE_IP_ADDRESS",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_MEDIUM,
            explanation="The domain resembles an IP address, which is uncommon for trusted sender identity and can be suspicious.",
        ),
        Finding(
            code="DOMAIN_HAS_SUSPICIOUS_TLD",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_MEDIUM,
            explanation="The domain uses a top-level domain that is more commonly associated with abuse or impersonation.",
        ),
    ]
