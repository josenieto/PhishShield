import json
from pathlib import Path

from tools.ml_data_preparation.phishshield_fixtures import (
    NORMALIZED_LABEL_BENIGN,
    NORMALIZED_LABEL_SUSPICIOUS,
)
from tools.ml_training.evaluate_fixture_holdout import (
    DEFAULT_FIXTURE_LABELS,
    evaluate_fixture_holdout,
    main,
)
from tools.ml_training.train_baseline import FEATURE_SET_TEXT


def test_should_evaluate_fixture_holdout(tmp_path: Path) -> None:
    training_path = _write_training_dataset(tmp_path)
    fixtures_dir = _write_fixture_dataset(tmp_path)

    result = evaluate_fixture_holdout(
        input_paths=[training_path],
        fixtures_dir=fixtures_dir,
        feature_set=FEATURE_SET_TEXT,
        random_seed=7,
        fixture_labels={
            "benign_sample.eml": NORMALIZED_LABEL_BENIGN,
            "suspicious_sample.eml": NORMALIZED_LABEL_SUSPICIOUS,
        },
    )

    assert result.total == 2
    assert 0 <= result.correct <= 2
    assert 0.0 <= result.accuracy <= 1.0
    assert result.false_positive_benign >= 0
    assert result.false_negative_suspicious >= 0
    assert {prediction.fixture_name for prediction in result.predictions} == {
        "benign_sample.eml",
        "suspicious_sample.eml",
    }
    assert all(prediction.suspicious_probability is None for prediction in result.predictions)


def test_should_evaluate_fixture_holdout_with_suspicious_threshold(tmp_path: Path) -> None:
    training_path = _write_training_dataset(tmp_path)
    fixtures_dir = _write_fixture_dataset(tmp_path)

    result = evaluate_fixture_holdout(
        input_paths=[training_path],
        fixtures_dir=fixtures_dir,
        feature_set=FEATURE_SET_TEXT,
        random_seed=7,
        fixture_labels={
            "benign_sample.eml": NORMALIZED_LABEL_BENIGN,
            "suspicious_sample.eml": NORMALIZED_LABEL_SUSPICIOUS,
        },
        suspicious_threshold=0.7,
    )

    assert result.total == 2
    assert all(
        prediction.suspicious_probability is not None
        and 0.0 <= prediction.suspicious_probability <= 1.0
        for prediction in result.predictions
    )


def test_should_report_metrics_by_family_from_holdout_manifest(tmp_path: Path) -> None:
    training_path = _write_training_dataset(tmp_path)
    fixtures_dir = _write_fixture_dataset(tmp_path)
    manifest_path = tmp_path / "holdout.jsonl"
    manifest_path.write_text(
        "\n".join(
            [
                json.dumps({
                    "path": "benign_sample.eml",
                    "expected_label": NORMALIZED_LABEL_BENIGN,
                    "family": "account",
                    "source": "independent-synthetic",
                }),
                json.dumps({
                    "path": "suspicious_sample.eml",
                    "expected_label": NORMALIZED_LABEL_SUSPICIOUS,
                    "family": "account",
                    "source": "independent-synthetic",
                }),
            ]
        ) + "\n",
        encoding="utf-8",
    )

    result = evaluate_fixture_holdout(
        input_paths=[training_path],
        fixtures_dir=fixtures_dir,
        feature_set=FEATURE_SET_TEXT,
        random_seed=7,
        holdout_manifest=manifest_path,
    )

    assert result.metrics_by_family["account"] == {
        "total": 2,
        "accuracy": 1.0,
        "benign_total": 1,
        "suspicious_total": 1,
        "false_positive_benign": 0,
        "false_negative_suspicious": 0,
    }
    assert all(prediction.source == "independent-synthetic" for prediction in result.predictions)


def test_should_reject_holdout_manifest_with_missing_fields(tmp_path: Path) -> None:
    training_path = _write_training_dataset(tmp_path)
    fixtures_dir = _write_fixture_dataset(tmp_path)
    manifest_path = tmp_path / "invalid-holdout.jsonl"
    manifest_path.write_text(json.dumps({"path": "benign_sample.eml"}) + "\n", encoding="utf-8")

    try:
        evaluate_fixture_holdout(
            input_paths=[training_path],
            fixtures_dir=fixtures_dir,
            feature_set=FEATURE_SET_TEXT,
            holdout_manifest=manifest_path,
        )
    except ValueError as error:
        assert "missing" in str(error)
    else:
        raise AssertionError("Expected invalid holdout manifest to be rejected")


def test_should_return_zero_exit_code_from_cli(tmp_path: Path) -> None:
    training_path = _write_training_dataset(tmp_path)
    fixtures_dir = _write_default_fixture_dataset(tmp_path)

    exit_code = main([
        "--input",
        str(training_path),
        "--fixtures-dir",
        str(fixtures_dir),
        "--feature-set",
        FEATURE_SET_TEXT,
        "--random-seed",
        "7",
    ])

    assert exit_code == 0


def test_should_return_zero_exit_code_from_cli_with_threshold(tmp_path: Path) -> None:
    training_path = _write_training_dataset(tmp_path)
    fixtures_dir = _write_default_fixture_dataset(tmp_path)

    exit_code = main([
        "--input",
        str(training_path),
        "--fixtures-dir",
        str(fixtures_dir),
        "--feature-set",
        FEATURE_SET_TEXT,
        "--random-seed",
        "7",
        "--suspicious-threshold",
        "0.7",
    ])

    assert exit_code == 0


def _write_training_dataset(tmp_path: Path) -> Path:
    input_path = tmp_path / "prepared.jsonl"
    rows = [
        _row("benign-1", "benign", "Project meeting", "Please review the project notes."),
        _row("benign-2", "benign", "Weekly report", "The weekly summary is attached."),
        _row("suspicious-1", "suspicious", "Verify your account", "Verify your account at the login page."),
        _row("suspicious-2", "suspicious", "Payment required", "Payment required immediately."),
    ]
    input_path.write_text("".join(rows), encoding="utf-8")

    return input_path


def _write_fixture_dataset(tmp_path: Path) -> Path:
    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir()
    (fixtures_dir / "benign_sample.eml").write_bytes(
        _email_bytes("Status update", "Please review the project notes.")
    )
    (fixtures_dir / "suspicious_sample.eml").write_bytes(
        _email_bytes("Verify your account", "Verify your account at the login page.")
    )

    return fixtures_dir


def _write_default_fixture_dataset(tmp_path: Path) -> Path:
    fixtures_dir = tmp_path / "default-fixtures"
    fixtures_dir.mkdir()

    for fixture_name, expected_label in DEFAULT_FIXTURE_LABELS.items():
        if expected_label == NORMALIZED_LABEL_BENIGN:
            fixture_bytes = _email_bytes("Status update", "Please review the project notes.")
        else:
            fixture_bytes = _email_bytes("Verify your account", "Verify your account at the login page.")

        (fixtures_dir / fixture_name).write_bytes(fixture_bytes)

    return fixtures_dir


def _row(sample_id: str, normalized_label: str, subject: str, body_text: str) -> str:
    return json.dumps(
        {
            "sample_id": sample_id,
            "source": "synthetic",
            "source_id": f"{sample_id}.eml",
            "source_uri": "synthetic://unit-test",
            "original_label": normalized_label,
            "normalized_label": normalized_label,
            "subject": subject,
            "body_text": body_text,
            "sender_domain": "example.com",
            "urls": [],
            "attachment_filenames": [],
            "raw_available": True,
            "metadata": {"original_label": normalized_label},
        },
        sort_keys=True,
    ) + "\n"


def _email_bytes(subject: str, body: str) -> bytes:
    return "\r\n".join(
        [
            "From: Fixture Team <fixture@example.com>",
            f"Subject: {subject}",
            "Content-Type: text/plain; charset=utf-8",
            "",
            body,
        ]
    ).encode("utf-8")
