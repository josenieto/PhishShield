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
    "DOMAIN_HAS_MIXED_SCRIPTS": Finding(
        code="DOMAIN_HAS_MIXED_SCRIPTS",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_HIGH,
    ),
    "DOMAIN_HAS_CONFUSABLE_CHARACTERS": Finding(
        code="DOMAIN_HAS_CONFUSABLE_CHARACTERS",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_HIGH,
    ),
    "DOMAIN_HAS_SUSPICIOUS_DEPTH": Finding(
        code="DOMAIN_HAS_SUSPICIOUS_DEPTH",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_MEDIUM,
    ),
    "DOMAIN_LOOKS_LIKE_IP_ADDRESS": Finding(
        code="DOMAIN_LOOKS_LIKE_IP_ADDRESS",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_MEDIUM,
    ),
    "DOMAIN_HAS_SUSPICIOUS_TLD": Finding(
        code="DOMAIN_HAS_SUSPICIOUS_TLD",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_MEDIUM,
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
    "ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION": Finding(
        code="ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION",
        category=FINDING_CATEGORY_ATTACHMENT,
        severity=FINDING_SEVERITY_MEDIUM,
    ),
    "ATTACHMENT_HAS_DOUBLE_EXTENSION": Finding(
        code="ATTACHMENT_HAS_DOUBLE_EXTENSION",
        category=FINDING_CATEGORY_ATTACHMENT,
        severity=FINDING_SEVERITY_HIGH,
    ),
    "ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS": Finding(
        code="ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS",
        category=FINDING_CATEGORY_ATTACHMENT,
        severity=FINDING_SEVERITY_HIGH,
    ),
    "AUTHENTICATION_DMARC_FAILED": Finding(
        code="AUTHENTICATION_DMARC_FAILED",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_CRITICAL,
    ),
    "AUTHENTICATION_SPF_FAILED": Finding(
        code="AUTHENTICATION_SPF_FAILED",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_HIGH,
    ),
    "AUTHENTICATION_DKIM_FAILED": Finding(
        code="AUTHENTICATION_DKIM_FAILED",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_HIGH,
    ),
    "AUTHENTICATION_HAS_MULTIPLE_FAILURES": Finding(
        code="AUTHENTICATION_HAS_MULTIPLE_FAILURES",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_CRITICAL,
    ),
    "AUTHENTICATION_RESULTS_UNKNOWN": Finding(
        code="AUTHENTICATION_RESULTS_UNKNOWN",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_MEDIUM,
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
