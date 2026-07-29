import json
from pathlib import Path

import joblib
import pytest

from tools.ml_training.export_baseline_artifact import export_baseline_artifact, main
from tools.ml_training.train_baseline import FEATURE_SET_TEXT_WITH_LIGHT_METADATA


def test_should_export_model_artifact_and_metadata(tmp_path: Path) -> None:
    input_path = _write_dataset(tmp_path)
    model_output = tmp_path / "models" / "candidate.joblib"
    metadata_output = tmp_path / "models" / "candidate.metadata.json"

    result = export_baseline_artifact(
        input_paths=[input_path],
        model_output_path=model_output,
        metadata_output_path=metadata_output,
        feature_set=FEATURE_SET_TEXT_WITH_LIGHT_METADATA,
        validation_ratio=0.25,
        random_seed=7,
        holdout_accuracy=0.875,
        holdout_false_positive_benign=3,
        holdout_false_negative_suspicious=1,
    )
    metadata = json.loads(metadata_output.read_text(encoding="utf-8"))
    model = joblib.load(model_output)
    prediction = model.predict(["Verify your account at https://example.com/login"])

    assert model_output.is_file()
    assert metadata_output.is_file()
    assert result.samples == 8
    assert metadata["model_name"] == "phishshield_baseline_candidate"
    assert metadata["model_type"] == "tfidf_logistic_regression"
    assert metadata["status"] == "experimental"
    assert metadata["feature_set"] == FEATURE_SET_TEXT_WITH_LIGHT_METADATA
    assert metadata["holdout_reference"] == {
        "name": "PhishShield 32-fixture notification holdout",
        "accuracy": 0.875,
        "false_negative_suspicious": 1,
        "false_positive_benign": 3,
    }
    assert "Runtime inference integration remains deferred." in metadata["limitations"]
    assert prediction[0] in {"benign", "suspicious"}


def test_should_reject_invalid_validation_ratio(tmp_path: Path) -> None:
    input_path = _write_dataset(tmp_path)

    with pytest.raises(ValueError, match="validation_ratio must be between 0.0 and 1.0"):
        export_baseline_artifact(
            input_paths=[input_path],
            model_output_path=tmp_path / "model.joblib",
            metadata_output_path=tmp_path / "metadata.json",
            validation_ratio=1.0,
        )


def test_should_return_zero_from_cli(tmp_path: Path) -> None:
    input_path = _write_dataset(tmp_path)
    model_output = tmp_path / "models" / "candidate.joblib"
    metadata_output = tmp_path / "models" / "candidate.metadata.json"

    exit_code = main([
        "--input",
        str(input_path),
        "--feature-set",
        FEATURE_SET_TEXT_WITH_LIGHT_METADATA,
        "--validation-ratio",
        "0.25",
        "--random-seed",
        "7",
        "--model-output",
        str(model_output),
        "--metadata-output",
        str(metadata_output),
        "--holdout-accuracy",
        "0.875",
        "--holdout-false-positive-benign",
        "3",
        "--holdout-false-negative-suspicious",
        "1",
    ])

    assert exit_code == 0
    assert model_output.is_file()
    assert metadata_output.is_file()


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
