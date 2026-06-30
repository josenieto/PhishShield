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


_FINDING_DEFINITIONS = {
    "DOMAIN_CONTAINS_PUNYCODE": Finding(
        code="DOMAIN_CONTAINS_PUNYCODE",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_HIGH,
    ),
    "URL_HAS_EMBEDDED_CREDENTIALS": Finding(
        code="URL_HAS_EMBEDDED_CREDENTIALS",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_HIGH,
    ),
    "URL_SCHEME_NOT_ALLOWED": Finding(
        code="URL_SCHEME_NOT_ALLOWED",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_MEDIUM,
    ),
    "URL_HAS_SUSPICIOUS_SCHEME": Finding(
        code="URL_HAS_SUSPICIOUS_SCHEME",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_HIGH,
    ),
    "URL_HAS_SUSPICIOUS_QUERY_DENSITY": Finding(
        code="URL_HAS_SUSPICIOUS_QUERY_DENSITY",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_MEDIUM,
    ),
    "URL_USES_KNOWN_SHORTENER_DOMAIN": Finding(
        code="URL_USES_KNOWN_SHORTENER_DOMAIN",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_MEDIUM,
    ),
    "ATTACHMENT_HAS_EXECUTABLE_EXTENSION": Finding(
        code="ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
        category=FINDING_CATEGORY_ATTACHMENT,
        severity=FINDING_SEVERITY_CRITICAL,
    ),
    "AUTHENTICATION_DMARC_FAILED": Finding(
        code="AUTHENTICATION_DMARC_FAILED",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_CRITICAL,
    ),
    "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS": Finding(
        code="SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS",
        category=FINDING_CATEGORY_SOCIAL_ENGINEERING,
        severity=FINDING_SEVERITY_HIGH,
    ),
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
