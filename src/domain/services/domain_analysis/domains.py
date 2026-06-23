def split_domain_labels(domain: str) -> list[str]:
    """Split a domain into meaningful labels."""
    normalized_domain = domain.strip().strip(".")

    if not normalized_domain:
        return []

    return [
        label
        for label in normalized_domain.split(".")
        if label
    ]
