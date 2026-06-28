SOCIAL_ENGINEERING_LOW = "LOW"
SOCIAL_ENGINEERING_MEDIUM = "MEDIUM"
SOCIAL_ENGINEERING_HIGH = "HIGH"
SOCIAL_ENGINEERING_CRITICAL = "CRITICAL"


def contains_urgency_terms(text: str, terms: set[str]) -> bool:
    """Return True when text contains any configured urgency term."""
    return _contains_any_term(text, terms)


def contains_financial_pressure_terms(text: str, terms: set[str]) -> bool:
    """Return True when text contains any configured financial pressure term."""
    return _contains_any_term(text, terms)


def contains_credential_request_terms(text: str, terms: set[str]) -> bool:
    """Return True when text contains any configured credential request term."""
    return _contains_any_term(text, terms)


def count_social_engineering_signals(
    text: str,
    signal_terms: dict[str, set[str]],
) -> dict[str, int]:
    """Return the number of configured social engineering terms found per category."""
    normalized_text = text.lower()

    return {
        category: sum(
            1
            for term in terms
            if (normalized_term := term.strip().lower())
            and normalized_term in normalized_text
        )
        for category, terms in signal_terms.items()
    }


def classify_social_engineering_risk(signal_counts: dict[str, int]) -> str:
    """Return a risk level from social engineering signal counts."""
    total_signals = sum(
        max(count, 0)
        for count in signal_counts.values()
    )

    if total_signals >= 3:
        return SOCIAL_ENGINEERING_CRITICAL

    if total_signals == 2:
        return SOCIAL_ENGINEERING_HIGH

    if total_signals == 1:
        return SOCIAL_ENGINEERING_MEDIUM

    return SOCIAL_ENGINEERING_LOW


def _contains_any_term(text: str, terms: set[str]) -> bool:
    normalized_text = text.lower()

    return any(
        normalized_term in normalized_text
        for term in terms
        if (normalized_term := term.strip().lower())
    )
