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


def _finding(code: str, category: str, severity: str) -> Finding:
    return Finding(
        code=code,
        category=category,
        severity=severity,
    )


_FINDING_DEFINITIONS = {
    finding.code: finding
    for finding in [
        _finding(
            "DOMAIN_CONTAINS_PUNYCODE",
            FINDING_CATEGORY_DOMAIN,
            FINDING_SEVERITY_HIGH,
        ),
        _finding(
            "DOMAIN_HAS_MIXED_SCRIPTS",
            FINDING_CATEGORY_DOMAIN,
            FINDING_SEVERITY_HIGH,
        ),
        _finding(
            "DOMAIN_HAS_CONFUSABLE_CHARACTERS",
            FINDING_CATEGORY_DOMAIN,
            FINDING_SEVERITY_HIGH,
        ),
        _finding(
            "DOMAIN_HAS_SUSPICIOUS_DEPTH",
            FINDING_CATEGORY_DOMAIN,
            FINDING_SEVERITY_MEDIUM,
        ),
        _finding(
            "DOMAIN_LOOKS_LIKE_IP_ADDRESS",
            FINDING_CATEGORY_DOMAIN,
            FINDING_SEVERITY_MEDIUM,
        ),
        _finding(
            "DOMAIN_HAS_SUSPICIOUS_TLD",
            FINDING_CATEGORY_DOMAIN,
            FINDING_SEVERITY_MEDIUM,
        ),
        _finding(
            "URL_HAS_EMBEDDED_CREDENTIALS",
            FINDING_CATEGORY_URL,
            FINDING_SEVERITY_HIGH,
        ),
        _finding(
            "URL_SCHEME_NOT_ALLOWED",
            FINDING_CATEGORY_URL,
            FINDING_SEVERITY_MEDIUM,
        ),
        _finding(
            "URL_HAS_SUSPICIOUS_SCHEME",
            FINDING_CATEGORY_URL,
            FINDING_SEVERITY_HIGH,
        ),
        _finding(
            "URL_HAS_SUSPICIOUS_QUERY_DENSITY",
            FINDING_CATEGORY_URL,
            FINDING_SEVERITY_MEDIUM,
        ),
        _finding(
            "URL_USES_KNOWN_SHORTENER_DOMAIN",
            FINDING_CATEGORY_URL,
            FINDING_SEVERITY_MEDIUM,
        ),
        _finding(
            "ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
            FINDING_CATEGORY_ATTACHMENT,
            FINDING_SEVERITY_CRITICAL,
        ),
        _finding(
            "ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION",
            FINDING_CATEGORY_ATTACHMENT,
            FINDING_SEVERITY_MEDIUM,
        ),
        _finding(
            "ATTACHMENT_HAS_DOUBLE_EXTENSION",
            FINDING_CATEGORY_ATTACHMENT,
            FINDING_SEVERITY_HIGH,
        ),
        _finding(
            "ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS",
            FINDING_CATEGORY_ATTACHMENT,
            FINDING_SEVERITY_HIGH,
        ),
        _finding(
            "AUTHENTICATION_DMARC_FAILED",
            FINDING_CATEGORY_AUTHENTICATION,
            FINDING_SEVERITY_CRITICAL,
        ),
        _finding(
            "AUTHENTICATION_SPF_FAILED",
            FINDING_CATEGORY_AUTHENTICATION,
            FINDING_SEVERITY_HIGH,
        ),
        _finding(
            "AUTHENTICATION_DKIM_FAILED",
            FINDING_CATEGORY_AUTHENTICATION,
            FINDING_SEVERITY_HIGH,
        ),
        _finding(
            "AUTHENTICATION_HAS_MULTIPLE_FAILURES",
            FINDING_CATEGORY_AUTHENTICATION,
            FINDING_SEVERITY_CRITICAL,
        ),
        _finding(
            "AUTHENTICATION_RESULTS_UNKNOWN",
            FINDING_CATEGORY_AUTHENTICATION,
            FINDING_SEVERITY_MEDIUM,
        ),
        _finding(
            "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS",
            FINDING_CATEGORY_SOCIAL_ENGINEERING,
            FINDING_SEVERITY_HIGH,
        ),
        _finding(
            "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS",
            FINDING_CATEGORY_SOCIAL_ENGINEERING,
            FINDING_SEVERITY_MEDIUM,
        ),
        _finding(
            "SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS",
            FINDING_CATEGORY_SOCIAL_ENGINEERING,
            FINDING_SEVERITY_MEDIUM,
        ),
    ]
}


def build_finding_from_code(code: str) -> Finding:
    """Return a Finding definition for a known code or an unknown fallback."""
    return _FINDING_DEFINITIONS.get(
        code,
        Finding(
            code=code,
            category=FINDING_CATEGORY_UNKNOWN,
            severity=FINDING_SEVERITY_UNKNOWN,
        ),
    )


def build_findings_from_codes(codes: list[str]) -> list[Finding]:
    """Return Finding definitions for finding codes while preserving input order."""
    return [
        build_finding_from_code(code)
        for code in codes
    ]
