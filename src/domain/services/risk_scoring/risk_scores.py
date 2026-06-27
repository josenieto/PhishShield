RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"


def calculate_indicator_score(
    indicators: list[str],
    weights: dict[str, int],
) -> int:
    """Return the sum of configured weights for the given indicators."""
    return sum(
        weights.get(indicator, 0)
        for indicator in indicators
    )


def combine_risk_scores(scores: list[int]) -> int:
    """Return the sum of partial risk scores."""
    return sum(scores)


def cap_risk_score(
    score: int,
    min_score: int = 0,
    max_score: int = 100,
) -> int:
    """Return a risk score capped to the configured inclusive range."""
    if min_score > max_score:
        raise ValueError("min_score must be less than or equal to max_score")

    return min(max(score, min_score), max_score)


def classify_risk_level(score: int) -> str:
    """Return a risk level for the given numeric score."""
    if score >= 75:
        return RISK_CRITICAL

    if score >= 50:
        return RISK_HIGH

    if score >= 25:
        return RISK_MEDIUM

    return RISK_LOW


def has_critical_indicators(
    indicators: list[str],
    critical_indicators: set[str],
) -> bool:
    """Return True when any indicator is marked as critical."""
    return any(
        indicator in critical_indicators
        for indicator in indicators
    )
