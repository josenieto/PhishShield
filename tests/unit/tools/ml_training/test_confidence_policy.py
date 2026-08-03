import pytest

from tools.ml_training.confidence_policy import classify_suspicious_probability


@pytest.mark.parametrize(
    ("probability", "label", "confidence"),
    [
        (0.10, "benign", 0.90),
        (0.50, "inconclusive", 0.50),
        (0.90, "suspicious", 0.90),
    ],
)
def test_should_classify_confidence_bands(probability: float, label: str, confidence: float) -> None:
    assert classify_suspicious_probability(probability) == (label, confidence)


def test_should_reject_invalid_confidence_bands() -> None:
    with pytest.raises(ValueError):
        classify_suspicious_probability(0.5, low_threshold=0.9, high_threshold=0.1)
