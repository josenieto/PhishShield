from typing import Literal


ConfidenceLabel = Literal["benign", "suspicious", "inconclusive"]


def classify_suspicious_probability(
    suspicious_probability: float,
    low_threshold: float = 0.15,
    high_threshold: float = 0.85,
) -> tuple[ConfidenceLabel, float]:
    if not 0.0 <= low_threshold < high_threshold <= 1.0:
        raise ValueError("confidence thresholds must satisfy 0 <= low < high <= 1")
    confidence = max(suspicious_probability, 1.0 - suspicious_probability)
    if suspicious_probability >= high_threshold:
        return "suspicious", confidence
    if suspicious_probability <= low_threshold:
        return "benign", confidence
    return "inconclusive", confidence
