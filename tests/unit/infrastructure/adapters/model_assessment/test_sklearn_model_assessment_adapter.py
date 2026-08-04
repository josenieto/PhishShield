import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from application.models.model_assessment import (
    MODEL_ASSESSMENT_LABEL_BENIGN,
    MODEL_ASSESSMENT_LABEL_INCONCLUSIVE,
    MODEL_ASSESSMENT_LABEL_SUSPICIOUS,
    MODEL_ASSESSMENT_LABEL_UNKNOWN,
    MODEL_ASSESSMENT_STATUS_COMPLETED,
    MODEL_ASSESSMENT_STATUS_FAILED,
    MODEL_ASSESSMENT_STATUS_INCONCLUSIVE,
    MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED,
)
from application.ports.outbound.model_assessment import (
    AssessRawEmailWithModelCommand,
    ModelAssessmentPort,
)
from infrastructure.adapters.model_assessment.sklearn_model_assessment_adapter import (
    SklearnModelAssessmentAdapter,
)


def test_should_return_not_configured_when_artifact_is_missing(tmp_path: Path) -> None:
    adapter = SklearnModelAssessmentAdapter(
        model_artifact_path=tmp_path / "missing.joblib",
        metadata_path=tmp_path / "missing.metadata.json",
    )

    assessment = adapter.assess_raw_email(_command(_email_bytes("Account summary", "Body.")))

    assert assessment.status == MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED
    assert assessment.label == MODEL_ASSESSMENT_LABEL_UNKNOWN
    assert assessment.confidence is None


def test_should_return_completed_assessment_with_configured_model(tmp_path: Path) -> None:
    model_path, metadata_path = _write_model_and_metadata(tmp_path)
    adapter: ModelAssessmentPort = SklearnModelAssessmentAdapter(
        model_artifact_path=model_path,
        metadata_path=metadata_path,
    )

    assessment = adapter.assess_raw_email(
        _command(_email_bytes("Verify your account", "Verify your account password now."))
    )

    assert assessment.status in {MODEL_ASSESSMENT_STATUS_COMPLETED, MODEL_ASSESSMENT_STATUS_INCONCLUSIVE}
    assert assessment.label in {
        MODEL_ASSESSMENT_LABEL_BENIGN,
        MODEL_ASSESSMENT_LABEL_SUSPICIOUS,
        MODEL_ASSESSMENT_LABEL_INCONCLUSIVE,
    }
    assert assessment.confidence is not None
    assert 0.0 <= assessment.confidence <= 1.0
    assert assessment.summary
    assert assessment.signals == (
        "Experimental sklearn baseline.",
        "Uses text_with_light_metadata features.",
        "Scope family: account.",
        "Deterministic scope gate.",
        "Deterministic analysis remains authoritative.",
    )
    assert assessment.model_name == "unit-test-model"
    assert assessment.model_version == "test-commit"
    assert assessment.error_message == ""


def test_should_return_failed_when_artifact_cannot_be_loaded(tmp_path: Path) -> None:
    model_path = tmp_path / "broken.joblib"
    metadata_path = tmp_path / "metadata.json"
    model_path.write_text("not a model", encoding="utf-8")
    _write_metadata(metadata_path)
    adapter = SklearnModelAssessmentAdapter(
        model_artifact_path=model_path,
        metadata_path=metadata_path,
    )

    assessment = adapter.assess_raw_email(_command(_email_bytes("Subject", "Body.")))

    assert assessment.status == MODEL_ASSESSMENT_STATUS_FAILED
    assert assessment.label == MODEL_ASSESSMENT_LABEL_UNKNOWN
    assert assessment.confidence is None
    assert assessment.error_message


def test_should_return_inconclusive_when_model_confidence_is_not_strong_enough(tmp_path: Path) -> None:
    model_path, metadata_path = _write_model_and_metadata(tmp_path)
    adapter = SklearnModelAssessmentAdapter(model_path, metadata_path)

    assessment = adapter.assess_raw_email(
        _command(_email_bytes("Account review", "Please review your account."))
    )

    assert assessment.status == MODEL_ASSESSMENT_STATUS_INCONCLUSIVE
    assert assessment.label == MODEL_ASSESSMENT_LABEL_INCONCLUSIVE
    assert assessment.confidence is not None
    assert "inconclusive" in assessment.summary


def test_should_return_failed_when_metadata_feature_set_is_unsupported(tmp_path: Path) -> None:
    model_path, metadata_path = _write_model_and_metadata(tmp_path, feature_set="text")
    adapter = SklearnModelAssessmentAdapter(
        model_artifact_path=model_path,
        metadata_path=metadata_path,
    )

    assessment = adapter.assess_raw_email(_command(_email_bytes("Subject", "Body.")))

    assert assessment.status == MODEL_ASSESSMENT_STATUS_FAILED
    assert assessment.error_message == "Unsupported model feature set"


def _write_model_and_metadata(tmp_path: Path, feature_set: str = "text_with_light_metadata") -> tuple[Path, Path]:
    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("classifier", LogisticRegression(max_iter=1_000)),
        ]
    )
    model.fit(
        [
            "Account activity summary is ready.",
            "Newsletter preferences were updated.",
            "Verify your account password now.",
            "Confirm your login to keep access.",
        ],
        ["benign", "benign", "suspicious", "suspicious"],
    )
    model_path = tmp_path / "model.joblib"
    metadata_path = tmp_path / "metadata.json"
    joblib.dump(model, model_path)
    _write_metadata(metadata_path, feature_set=feature_set)

    return model_path, metadata_path


def _write_metadata(metadata_path: Path, feature_set: str = "text_with_light_metadata") -> None:
    metadata_path.write_text(
        json.dumps(
            {
                "model_name": "unit-test-model",
                "git_commit": "test-commit",
                "created_at": "2026-07-12T00:00:00Z",
                "feature_set": feature_set,
            }
        ),
        encoding="utf-8",
    )


def _command(raw_email: bytes) -> AssessRawEmailWithModelCommand:
    return AssessRawEmailWithModelCommand(
        raw_email=raw_email,
        filename="sample.eml",
        content_type="message/rfc822",
        max_input_bytes=100_000,
    )


def _email_bytes(subject: str, body: str) -> bytes:
    return "\r\n".join(
        [
            "From: Sender <sender@example.com>",
            f"Subject: {subject}",
            "Content-Type: text/plain; charset=utf-8",
            "",
            body,
        ]
    ).encode("utf-8")
