import json
from pathlib import Path

from tools.ml_training.evaluate_prepared_holdout import evaluate_prepared_holdout
from tools.ml_training.train_baseline import FEATURE_SET_TEXT_WITH_LIGHT_METADATA


def test_should_evaluate_prepared_holdout_by_label_and_quality_dimensions(tmp_path: Path) -> None:
    training = tmp_path / "training.jsonl"
    holdout = tmp_path / "holdout.jsonl"
    training.write_text("\n".join(json.dumps(row) for row in [
        _row("b1", "benign", "Account summary", "Your account summary is ready."),
        _row("b2", "benign", "Newsletter", "Here is your weekly newsletter."),
        _row("s1", "suspicious", "Verify account", "Verify your account now https://evil.test/login."),
        _row("s2", "suspicious", "Payment required", "Payment required immediately https://evil.test/pay."),
    ]) + "\n", encoding="utf-8")
    holdout.write_text("\n".join(json.dumps(row) for row in [
        _row("h1", "benign", "Account summary", "Your account summary is ready."),
        _row("h2", "suspicious", "Verify account", "Verify your account now https://evil.test/login."),
    ]) + "\n", encoding="utf-8")

    result = evaluate_prepared_holdout([training], holdout, FEATURE_SET_TEXT_WITH_LIGHT_METADATA)

    assert result.total == 2
    assert set(result.metrics_by("expected_label")) == {"benign", "suspicious"}
    assert set(result.metrics_by("family")) == {"unclassified"}
    assert set(result.metrics_by("body_length_bucket")) == {"short_lt_300"}
    assert result.predictions[0].source == "ceas_08"
    assert 0.0 <= result.abstention_rate <= 1.0
    assert 0.0 <= result.conditional_accuracy <= 1.0
    assert 0.0 <= result.confident_false_positive_rate <= 1.0
    assert 0.0 <= result.confident_false_negative_rate <= 1.0


def _row(sample_id: str, label: str, subject: str, body: str) -> dict[str, object]:
    return {
        "sample_id": sample_id,
        "source": "ceas_08",
        "normalized_label": label,
        "subject": subject,
        "body_text": body,
        "urls": ["https://evil.test/login"] if "evil.test" in body else [],
        "attachment_filenames": [],
        "metadata": {"source_urls_flag": "1"},
    }
