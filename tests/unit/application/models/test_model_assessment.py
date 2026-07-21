from dataclasses import FrozenInstanceError

import pytest

from application.models.model_assessment import (
    MODEL_ASSESSMENT_LABEL_PHISHING,
    MODEL_ASSESSMENT_LABEL_UNKNOWN,
    MODEL_ASSESSMENT_STATUS_COMPLETED,
    MODEL_ASSESSMENT_STATUS_FAILED,
    ModelAssessment,
)


def test_should_store_completed_model_assessment() -> None:
    assessment = ModelAssessment(
        status=MODEL_ASSESSMENT_STATUS_COMPLETED,
        label=MODEL_ASSESSMENT_LABEL_PHISHING,
        confidence=0.84,
        summary="The message resembles a phishing lure.",
        signals=("Credential request wording", "Suspicious link presentation"),
        model_name="local-model",
        model_version="0.1",
    )

    assert assessment.status == MODEL_ASSESSMENT_STATUS_COMPLETED
    assert assessment.label == MODEL_ASSESSMENT_LABEL_PHISHING
    assert assessment.confidence == 0.84
    assert assessment.summary == "The message resembles a phishing lure."
    assert assessment.signals == (
        "Credential request wording",
        "Suspicious link presentation",
    )
    assert assessment.model_name == "local-model"
    assert assessment.model_version == "0.1"
    assert assessment.error_message == ""


def test_should_allow_missing_confidence() -> None:
    assessment = ModelAssessment(
        status=MODEL_ASSESSMENT_STATUS_FAILED,
        label=MODEL_ASSESSMENT_LABEL_UNKNOWN,
        confidence=None,
        summary="",
        signals=(),
        model_name="local-model",
        model_version="0.1",
        error_message="Model assessment timed out.",
    )

    assert assessment.confidence is None
    assert assessment.error_message == "Model assessment timed out."


def test_should_convert_signals_to_tuple() -> None:
    assessment = ModelAssessment(
        status=MODEL_ASSESSMENT_STATUS_COMPLETED,
        label=MODEL_ASSESSMENT_LABEL_PHISHING,
        confidence=0.65,
        summary="Suspicious message.",
        signals=["Urgency wording", "Credential request"],
        model_name="local-model",
        model_version="0.1",
    )

    assert assessment.signals == ("Urgency wording", "Credential request")
    assert isinstance(assessment.signals, tuple)


def test_should_reject_confidence_below_zero() -> None:
    with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
        ModelAssessment(
            status=MODEL_ASSESSMENT_STATUS_COMPLETED,
            label=MODEL_ASSESSMENT_LABEL_PHISHING,
            confidence=-0.01,
            summary="Invalid confidence.",
            signals=(),
            model_name="local-model",
            model_version="0.1",
        )


def test_should_reject_confidence_above_one() -> None:
    with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
        ModelAssessment(
            status=MODEL_ASSESSMENT_STATUS_COMPLETED,
            label=MODEL_ASSESSMENT_LABEL_PHISHING,
            confidence=1.01,
            summary="Invalid confidence.",
            signals=(),
            model_name="local-model",
            model_version="0.1",
        )


def test_should_be_immutable() -> None:
    assessment = ModelAssessment(
        status=MODEL_ASSESSMENT_STATUS_COMPLETED,
        label=MODEL_ASSESSMENT_LABEL_PHISHING,
        confidence=0.91,
        summary="Suspicious message.",
        signals=(),
        model_name="local-model",
        model_version="0.1",
    )

    with pytest.raises(FrozenInstanceError):
        assessment.label = MODEL_ASSESSMENT_LABEL_UNKNOWN
