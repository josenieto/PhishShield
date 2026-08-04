from tools.ml_training.promotion_policy import assess_family_promotion


def test_should_promote_family_meeting_approved_thresholds() -> None:
    promoted, reasons = assess_family_promotion(_metrics())

    assert promoted
    assert reasons == []


def test_should_reject_family_with_confident_errors() -> None:
    metrics = _metrics()
    metrics["confident_false_negative_rate"] = 0.10

    promoted, reasons = assess_family_promotion(metrics)

    assert not promoted
    assert "confident false-negative rate above 0.05" in reasons


def _metrics() -> dict[str, float | int]:
    return {
        "total": 40,
        "coverage": 0.70,
        "conditional_accuracy": 0.95,
        "confident_false_positive_rate": 0.05,
        "confident_false_negative_rate": 0.05,
    }
