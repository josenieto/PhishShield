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


def is_punycode_label(label: str) -> bool:
    """Return True when a domain label starts with the Punycode prefix."""
    return label.lower().startswith("xn--")
