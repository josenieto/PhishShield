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


def _finding(code: str, category: str, severity: str, explanation: str) -> Finding:
    return Finding(
        code=code,
        category=category,
        severity=severity,
        explanation=explanation,
    )


_FINDING_DEFINITIONS = {
    finding.code: finding
    for finding in [
        _finding(
            "DOMAIN_CONTAINS_PUNYCODE",
            FINDING_CATEGORY_DOMAIN,
            FINDING_SEVERITY_HIGH,
            "The domain contains Punycode, which can be used to create visually deceptive lookalike domains.",
        ),
        _finding(
            "DOMAIN_HAS_MIXED_SCRIPTS",
            FINDING_CATEGORY_DOMAIN,
            FINDING_SEVERITY_HIGH,
            "The domain mixes characters from multiple writing systems, which can indicate an impersonation attempt.",
        ),
        _finding(
            "DOMAIN_HAS_CONFUSABLE_CHARACTERS",
            FINDING_CATEGORY_DOMAIN,
            FINDING_SEVERITY_HIGH,
            "The domain contains characters that can visually imitate trusted brand names or domains.",
        ),
        _finding(
            "DOMAIN_HAS_SUSPICIOUS_DEPTH",
            FINDING_CATEGORY_DOMAIN,
            FINDING_SEVERITY_MEDIUM,
            "The domain has an unusually deep subdomain structure, which can be used to disguise the true host.",
        ),
        _finding(
            "DOMAIN_LOOKS_LIKE_IP_ADDRESS",
            FINDING_CATEGORY_DOMAIN,
            FINDING_SEVERITY_MEDIUM,
            "The domain resembles an IP address, which is uncommon for trusted sender identity and can be suspicious.",
        ),
        _finding(
            "DOMAIN_HAS_SUSPICIOUS_TLD",
            FINDING_CATEGORY_DOMAIN,
            FINDING_SEVERITY_MEDIUM,
            "The domain uses a top-level domain that is more commonly associated with abuse or impersonation.",
        ),
        _finding(
            "URL_HAS_EMBEDDED_CREDENTIALS",
            FINDING_CATEGORY_URL,
            FINDING_SEVERITY_HIGH,
            "The URL includes embedded credentials, which can hide the real destination and mislead the user.",
        ),
        _finding(
            "URL_SCHEME_NOT_ALLOWED",
            FINDING_CATEGORY_URL,
            FINDING_SEVERITY_MEDIUM,
            "The URL uses a scheme outside the allowed set, which may indicate an unsafe or unexpected destination.",
        ),
        _finding(
            "URL_HAS_SUSPICIOUS_SCHEME",
            FINDING_CATEGORY_URL,
            FINDING_SEVERITY_HIGH,
            "The URL uses a suspicious scheme that is not typical for normal web navigation.",
        ),
        _finding(
            "URL_HAS_SUSPICIOUS_QUERY_DENSITY",
            FINDING_CATEGORY_URL,
            FINDING_SEVERITY_MEDIUM,
            "The URL contains an unusually dense query string, which can be used to obfuscate tracking or malicious parameters.",
        ),
        _finding(
            "URL_USES_KNOWN_SHORTENER_DOMAIN",
            FINDING_CATEGORY_URL,
            FINDING_SEVERITY_MEDIUM,
            "The URL uses a known shortening service, which can hide the final destination from the user.",
        ),
        _finding(
            "ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
            FINDING_CATEGORY_ATTACHMENT,
            FINDING_SEVERITY_CRITICAL,
            "The attachment filename ends with an executable extension, which can deliver malware if opened.",
        ),
        _finding(
            "ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION",
            FINDING_CATEGORY_ATTACHMENT,
            FINDING_SEVERITY_MEDIUM,
            "The attachment is an Office-style document, which can carry embedded active content in some attack chains.",
        ),
        _finding(
            "ATTACHMENT_HAS_DOUBLE_EXTENSION",
            FINDING_CATEGORY_ATTACHMENT,
            FINDING_SEVERITY_HIGH,
            "The attachment uses a double extension, which can disguise the real file type and trick the user.",
        ),
        _finding(
            "ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS",
            FINDING_CATEGORY_ATTACHMENT,
            FINDING_SEVERITY_HIGH,
            "The attachment filename contains unusual characters that can be used to confuse file appearance or intent.",
        ),
        _finding(
            "AUTHENTICATION_DMARC_FAILED",
            FINDING_CATEGORY_AUTHENTICATION,
            FINDING_SEVERITY_CRITICAL,
            "DMARC authentication failed, which can indicate that the message does not align with the claimed sender domain policy.",
        ),
        _finding(
            "AUTHENTICATION_SPF_FAILED",
            FINDING_CATEGORY_AUTHENTICATION,
            FINDING_SEVERITY_HIGH,
            "SPF authentication failed, which can indicate that the sending server was not authorized for the claimed sender domain.",
        ),
        _finding(
            "AUTHENTICATION_DKIM_FAILED",
            FINDING_CATEGORY_AUTHENTICATION,
            FINDING_SEVERITY_HIGH,
            "DKIM authentication failed, which can indicate message tampering or an unauthorized sending path.",
        ),
        _finding(
            "AUTHENTICATION_HAS_MULTIPLE_FAILURES",
            FINDING_CATEGORY_AUTHENTICATION,
            FINDING_SEVERITY_CRITICAL,
            "Multiple authentication mechanisms failed, which strongly increases the risk that the message is spoofed.",
        ),
        _finding(
            "AUTHENTICATION_RESULTS_UNKNOWN",
            FINDING_CATEGORY_AUTHENTICATION,
            FINDING_SEVERITY_MEDIUM,
            "Authentication results were unavailable or could not be extracted, which reduces trust in sender validation.",
        ),
        _finding(
            "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS",
            FINDING_CATEGORY_SOCIAL_ENGINEERING,
            FINDING_SEVERITY_HIGH,
            "The message asks for account verification or credentials, which is a common phishing tactic.",
        ),
        _finding(
            "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS",
            FINDING_CATEGORY_SOCIAL_ENGINEERING,
            FINDING_SEVERITY_MEDIUM,
            "The message uses urgency language to pressure the recipient into acting quickly.",
        ),
        _finding(
            "SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS",
            FINDING_CATEGORY_SOCIAL_ENGINEERING,
            FINDING_SEVERITY_MEDIUM,
            "The message uses financial pressure language to push the recipient toward immediate action.",
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
            explanation="No explanation is available for this finding code yet.",
        ),
    )


def build_findings_from_codes(codes: list[str]) -> list[Finding]:
    """Return Finding definitions for finding codes while preserving input order."""
    return [
        build_finding_from_code(code)
        for code in codes
    ]
