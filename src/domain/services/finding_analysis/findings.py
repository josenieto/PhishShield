from domain.value_objects.finding import (
    FINDING_SEVERITY_CRITICAL,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_LOW,
    FINDING_SEVERITY_MEDIUM,
    FINDING_SEVERITY_UNKNOWN,
    Finding,
)


_SEVERITY_ORDER = {
    FINDING_SEVERITY_CRITICAL: 0,
    FINDING_SEVERITY_HIGH: 1,
    FINDING_SEVERITY_MEDIUM: 2,
    FINDING_SEVERITY_LOW: 3,
    FINDING_SEVERITY_UNKNOWN: 4,
}


def deduplicate_finding_codes(finding_codes: list[str]) -> list[str]:
    """Return finding codes without duplicates while preserving first occurrence order."""
    seen_finding_codes = set()
    deduplicated_finding_codes = []

    for finding_code in finding_codes:
        if finding_code not in seen_finding_codes:
            seen_finding_codes.add(finding_code)
            deduplicated_finding_codes.append(finding_code)

    return deduplicated_finding_codes


def filter_findings_by_category(
    findings: list[Finding],
    category: str,
) -> list[Finding]:
    """Return findings that match the given category exactly."""
    return [
        finding
        for finding in findings
        if finding.category == category
    ]


def count_findings_by_category(findings: list[Finding]) -> dict[str, int]:
    """Return finding counts grouped by exact category."""
    category_counts: dict[str, int] = {}

    for finding in findings:
        category_counts[finding.category] = category_counts.get(finding.category, 0) + 1

    return category_counts


def sort_findings_by_severity(findings: list[Finding]) -> list[Finding]:
    """Return findings sorted from highest to lowest severity."""
    return sorted(
        findings,
        key=lambda finding: _SEVERITY_ORDER.get(
            finding.severity,
            _SEVERITY_ORDER[FINDING_SEVERITY_UNKNOWN],
        ),
    )


def get_highest_finding_severity(findings: list[Finding]) -> str:
    """Return the highest recognized severity in a list of findings."""
    sorted_findings = sort_findings_by_severity(findings)

    for finding in sorted_findings:
        if finding.severity in _SEVERITY_ORDER:
            return finding.severity

    return FINDING_SEVERITY_UNKNOWN
