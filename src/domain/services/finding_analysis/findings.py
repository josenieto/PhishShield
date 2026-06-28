def deduplicate_finding_codes(finding_codes: list[str]) -> list[str]:
    """Return finding codes without duplicates while preserving first occurrence order."""
    seen_finding_codes = set()
    deduplicated_finding_codes = []

    for finding_code in finding_codes:
        if finding_code not in seen_finding_codes:
            seen_finding_codes.add(finding_code)
            deduplicated_finding_codes.append(finding_code)

    return deduplicated_finding_codes
