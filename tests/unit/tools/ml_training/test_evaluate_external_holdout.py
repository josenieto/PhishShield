import json
from pathlib import Path

from tools.ml_training.evaluate_external_holdout import (
    _row_to_text,
    evaluate_external_holdout,
)
from tools.ml_training.train_baseline import FEATURE_SET_TEXT_WITH_LIGHT_METADATA


def test_should_evaluate_external_jsonl_holdout_by_metadata_dimensions(tmp_path: Path) -> None:
    training_path = tmp_path / "training.jsonl"
    training_path.write_text(
        "\n".join(
            json.dumps(row)
            for row in [
                _prepared_row("b1", "benign", "Account summary", "Your account summary is ready."),
                _prepared_row("b2", "benign", "Newsletter", "Here is your weekly newsletter."),
                _prepared_row("s1", "suspicious", "Verify account", "Verify your account password immediately."),
                _prepared_row("s2", "suspicious", "Confirm payment", "Confirm your payment at the login portal."),
            ]
        ) + "\n",
        encoding="utf-8",
    )
    holdout_path = tmp_path / "external.jsonl"
    holdout_path.write_text(
        "\n".join(
            json.dumps(row)
            for row in [
                {"id": "external-benign", "subject": "Account summary", "body": "Your account summary is ready.", "label": "benign", "intent": "Informational", "technique": "None", "target": "Corporate"},
                {"id": "external-phishing", "subject": "Verify account", "body": "Verify your account password immediately.", "label": "phishing", "intent": "Credential Harvesting", "technique": "Fake Login", "target": "Corporate"},
            ]
        ) + "\n",
        encoding="utf-8",
    )

    result = evaluate_external_holdout(
        input_paths=[training_path],
        holdout_path=holdout_path,
        feature_set=FEATURE_SET_TEXT_WITH_LIGHT_METADATA,
    )

    assert result.total == 2
    assert set(result.metrics_by("expected_label")) == {"benign", "suspicious"}
    assert result.metrics_by("target")["Corporate"]["total"] == 2
    assert {prediction.source for prediction in result.predictions} == {"external-holdout"}


def test_should_keep_external_metadata_out_of_model_input() -> None:
    text = _row_to_text(
        {
            "subject": "Account update",
            "body": "Please review your account.",
            "spoofed_sender": "attacker@example.test",
            "target": "Banking",
            "technique": "Credential harvesting",
        },
        FEATURE_SET_TEXT_WITH_LIGHT_METADATA,
    )

    assert text == "Account update\nPlease review your account."
    assert "Banking" not in text
    assert "Credential harvesting" not in text


def test_should_extract_external_body_urls_with_runtime_parser() -> None:
    text = _row_to_text(
        {
            "subject": "Account update",
            "body": "Review https://example.test/account now.",
            "target": "Banking",
            "technique": "Credential harvesting",
        },
        FEATURE_SET_TEXT_WITH_LIGHT_METADATA,
    )

    assert text == (
        "Account update\n"
        "Review https://example.test/account now.\n"
        "https://example.test/account"
    )
    assert "Banking" not in text
    assert "Credential harvesting" not in text


def test_should_report_coverage_when_abstention_is_enabled(tmp_path: Path) -> None:
    training_path = tmp_path / "training.jsonl"
    holdout_path = tmp_path / "holdout.jsonl"
    holdout_rows = [
        {"id": "b1", "label": "benign", "subject": "Account summary", "body": "Your account summary is ready."},
        {"id": "b2", "label": "benign", "subject": "Newsletter", "body": "Weekly newsletter update."},
        {"id": "s1", "label": "phishing", "subject": "Verify account", "body": "Verify your account password now."},
        {"id": "s2", "label": "phishing", "subject": "Payment required", "body": "Payment required immediately."},
    ]
    training_rows = [
        _prepared_row("tb1", "benign", "Account summary", "Your account summary is ready."),
        _prepared_row("tb2", "benign", "Newsletter", "Weekly newsletter update."),
        _prepared_row("ts1", "suspicious", "Verify account", "Verify your account password now."),
        _prepared_row("ts2", "suspicious", "Payment required", "Payment required immediately."),
    ]
    training_path.write_text("\n".join(json.dumps(row) for row in training_rows) + "\n", encoding="utf-8")
    holdout_path.write_text("\n".join(json.dumps(row) for row in holdout_rows[2:]) + "\n", encoding="utf-8")

    result = evaluate_external_holdout(
        [training_path], holdout_path, FEATURE_SET_TEXT_WITH_LIGHT_METADATA
    )

    assert 0.0 <= result.coverage <= 1.0
    assert result.inconclusive >= 0
    assert 0.0 <= result.abstention_rate <= 1.0
    assert 0.0 <= result.conditional_accuracy <= 1.0
    assert 0.0 <= result.confident_false_positive_rate <= 1.0
    assert 0.0 <= result.confident_false_negative_rate <= 1.0


def _prepared_row(sample_id: str, label: str, subject: str, body: str) -> dict[str, object]:
    return {
        "sample_id": sample_id,
        "normalized_label": label,
        "subject": subject,
        "body_text": body,
        "urls": [],
        "attachment_filenames": [],
    }
