from domain.services.finding_analysis.finding_definitions import (
    build_finding_from_code,
    build_findings_from_codes,
)
from domain.value_objects.finding import (
    FINDING_CATEGORY_ATTACHMENT,
    FINDING_CATEGORY_AUTHENTICATION,
    FINDING_CATEGORY_DOMAIN,
    FINDING_CATEGORY_SOCIAL_ENGINEERING,
    FINDING_CATEGORY_UNKNOWN,
    FINDING_CATEGORY_URL,
    FINDING_SEVERITY_CRITICAL,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_MEDIUM,
    FINDING_SEVERITY_UNKNOWN,
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


def test_should_build_known_url_finding_from_code() -> None:
    assert build_finding_from_code("URL_HAS_EMBEDDED_CREDENTIALS") == Finding(
        code="URL_HAS_EMBEDDED_CREDENTIALS",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_build_url_scheme_not_allowed_finding_from_code() -> None:
    assert build_finding_from_code("URL_SCHEME_NOT_ALLOWED") == Finding(
        code="URL_SCHEME_NOT_ALLOWED",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_MEDIUM,
    )


def test_should_build_suspicious_url_scheme_finding_from_code() -> None:
    assert build_finding_from_code("URL_HAS_SUSPICIOUS_SCHEME") == Finding(
        code="URL_HAS_SUSPICIOUS_SCHEME",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_build_suspicious_url_query_density_finding_from_code() -> None:
    assert build_finding_from_code("URL_HAS_SUSPICIOUS_QUERY_DENSITY") == Finding(
        code="URL_HAS_SUSPICIOUS_QUERY_DENSITY",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_MEDIUM,
    )


def test_should_build_known_url_shortener_finding_from_code() -> None:
    assert build_finding_from_code("URL_USES_KNOWN_SHORTENER_DOMAIN") == Finding(
        code="URL_USES_KNOWN_SHORTENER_DOMAIN",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_MEDIUM,
    )


def test_should_build_known_attachment_finding_from_code() -> None:
    assert build_finding_from_code("ATTACHMENT_HAS_EXECUTABLE_EXTENSION") == Finding(
        code="ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
        category=FINDING_CATEGORY_ATTACHMENT,
        severity=FINDING_SEVERITY_CRITICAL,
    )


def test_should_build_known_authentication_finding_from_code() -> None:
    assert build_finding_from_code("AUTHENTICATION_DMARC_FAILED") == Finding(
        code="AUTHENTICATION_DMARC_FAILED",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_CRITICAL,
    )


def test_should_build_known_social_engineering_finding_from_code() -> None:
    assert build_finding_from_code(
        "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS"
    ) == Finding(
        code="SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS",
        category=FINDING_CATEGORY_SOCIAL_ENGINEERING,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_build_unknown_finding_from_unmapped_code() -> None:
    assert build_finding_from_code("UNKNOWN_FINDING_CODE") == Finding(
        code="UNKNOWN_FINDING_CODE",
        category=FINDING_CATEGORY_UNKNOWN,
        severity=FINDING_SEVERITY_UNKNOWN,
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
        ),
        Finding(
            code="URL_HAS_EMBEDDED_CREDENTIALS",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_HIGH,
        ),
        Finding(
            code="AUTHENTICATION_DMARC_FAILED",
            category=FINDING_CATEGORY_AUTHENTICATION,
            severity=FINDING_SEVERITY_CRITICAL,
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
        ),
        Finding(
            code="DOMAIN_CONTAINS_PUNYCODE",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_HIGH,
        ),
    ]


def test_should_return_empty_list_when_building_findings_from_empty_codes() -> None:
    assert build_findings_from_codes([]) == []


def test_should_build_url_findings_from_codes_preserving_order() -> None:
    assert build_findings_from_codes(
        [
            "URL_SCHEME_NOT_ALLOWED",
            "URL_HAS_SUSPICIOUS_SCHEME",
            "URL_HAS_EMBEDDED_CREDENTIALS",
            "URL_HAS_SUSPICIOUS_QUERY_DENSITY",
            "URL_USES_KNOWN_SHORTENER_DOMAIN",
        ]
    ) == [
        Finding(
            code="URL_SCHEME_NOT_ALLOWED",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_MEDIUM,
        ),
        Finding(
            code="URL_HAS_SUSPICIOUS_SCHEME",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_HIGH,
        ),
        Finding(
            code="URL_HAS_EMBEDDED_CREDENTIALS",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_HIGH,
        ),
        Finding(
            code="URL_HAS_SUSPICIOUS_QUERY_DENSITY",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_MEDIUM,
        ),
        Finding(
            code="URL_USES_KNOWN_SHORTENER_DOMAIN",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_MEDIUM,
        ),
    ]


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
