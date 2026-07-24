import json
from pathlib import Path

from tools.ml_training.train_baseline import (
    FEATURE_SET_TEXT,
    FEATURE_SET_TEXT_WITH_LIGHT_METADATA,
    main,
    train_baseline,
)


def test_should_train_balanced_text_baseline(tmp_path: Path) -> None:
    input_path = _write_dataset(tmp_path)

    result = train_baseline(
        input_paths=[input_path],
        feature_set=FEATURE_SET_TEXT,
        validation_ratio=0.25,
        random_seed=7,
    )

    assert result.total_samples == 8
    assert result.train_samples == 6
    assert result.validation_samples == 2
    assert result.label_distribution == {"benign": 4, "suspicious": 4}
    assert 0.0 <= result.accuracy <= 1.0
    assert 0.0 <= result.precision_suspicious <= 1.0
    assert 0.0 <= result.recall_suspicious <= 1.0
    assert 0.0 <= result.f1_suspicious <= 1.0
    assert len(result.confusion_matrix_values) == 2


def test_should_train_lightweight_metadata_baseline(tmp_path: Path) -> None:
    input_path = _write_dataset(tmp_path)

    result = train_baseline(
        input_paths=[input_path],
        feature_set=FEATURE_SET_TEXT_WITH_LIGHT_METADATA,
        validation_ratio=0.25,
        random_seed=7,
    )

    assert result.total_samples == 8
    assert result.label_distribution == {"benign": 4, "suspicious": 4}


def test_should_return_zero_exit_code_from_cli(tmp_path: Path) -> None:
    input_path = _write_dataset(tmp_path)

    exit_code = main([
        "--input",
        str(input_path),
        "--feature-set",
        FEATURE_SET_TEXT,
        "--validation-ratio",
        "0.25",
        "--random-seed",
        "7",
    ])

    assert exit_code == 0


def _write_dataset(tmp_path: Path) -> Path:
    input_path = tmp_path / "prepared.jsonl"
    rows = [
        _row("benign-1", "benign", "Project meeting", "Please review the project notes."),
        _row("benign-2", "benign", "Weekly report", "The weekly summary is attached."),
        _row("benign-3", "benign", "Lunch update", "The team lunch is scheduled for Friday."),
        _row("benign-4", "benign", "Build complete", "The build completed successfully."),
        _row("suspicious-1", "suspicious", "Verify your account", "Verify your account at the login page.", urls=["https://example.com/login"]),
        _row("suspicious-2", "suspicious", "Payment required", "Payment required immediately to avoid account lock."),
        _row("suspicious-3", "suspicious", "Confirm your login", "Confirm your login details now."),
        _row("suspicious-4", "suspicious", "Invoice overdue", "Invoice overdue and payment required."),
    ]
    input_path.write_text("".join(rows), encoding="utf-8")

    return input_path


def _row(
    sample_id: str,
    normalized_label: str,
    subject: str,
    body_text: str,
    urls: list[str] | None = None,
) -> str:
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
            "urls": [] if urls is None else urls,
            "attachment_filenames": [],
            "raw_available": True,
            "metadata": {"original_label": normalized_label},
        },
        sort_keys=True,
    ) + "\n"
