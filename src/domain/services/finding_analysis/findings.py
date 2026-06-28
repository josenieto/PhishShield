from domain.value_objects.finding import Finding


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
