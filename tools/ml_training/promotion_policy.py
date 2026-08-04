"""Promotion policy for the advisory model's independent holdout."""

from typing import Mapping


MIN_COVERAGE = 0.70
MIN_CONDITIONAL_ACCURACY = 0.95
MAX_CONFIDENT_FALSE_POSITIVE_RATE = 0.05
MAX_CONFIDENT_FALSE_NEGATIVE_RATE = 0.05
MIN_CONCLUSIVE_PREDICTIONS = 28


def assess_family_promotion(metrics: Mapping[str, float | int]) -> tuple[bool, list[str]]:
    """Return whether one family meets all approved promotion thresholds."""
    reasons: list[str] = []
    if int(metrics.get("total", 0)) != 40:
        reasons.append("family total must be 40")
    if int(metrics.get("total", 0) * float(metrics.get("coverage", 0.0))) < MIN_CONCLUSIVE_PREDICTIONS:
        reasons.append("coverage must yield at least 28 conclusive predictions")
    if float(metrics.get("coverage", 0.0)) < MIN_COVERAGE:
        reasons.append("coverage below 0.70")
    if float(metrics.get("conditional_accuracy", 0.0)) < MIN_CONDITIONAL_ACCURACY:
        reasons.append("conditional accuracy below 0.95")
    if float(metrics.get("confident_false_positive_rate", 0.0)) > MAX_CONFIDENT_FALSE_POSITIVE_RATE:
        reasons.append("confident false-positive rate above 0.05")
    if float(metrics.get("confident_false_negative_rate", 0.0)) > MAX_CONFIDENT_FALSE_NEGATIVE_RATE:
        reasons.append("confident false-negative rate above 0.05")
    return not reasons, reasons
