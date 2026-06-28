def deduplicate_findings(findings: list[str]) -> list[str]:
    """Return findings without duplicates while preserving first occurrence order."""
    seen_findings = set()
    deduplicated_findings = []

    for finding in findings:
        if finding not in seen_findings:
            seen_findings.add(finding)
            deduplicated_findings.append(finding)

    return deduplicated_findings
