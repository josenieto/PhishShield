import json
from pathlib import Path
from typing import Any

import joblib

from application.models.extracted_email import ExtractedEmailContent
from application.models.model_assessment import (
    MODEL_ASSESSMENT_LABEL_BENIGN,
    MODEL_ASSESSMENT_LABEL_INCONCLUSIVE,
    MODEL_ASSESSMENT_LABEL_SUSPICIOUS,
    MODEL_ASSESSMENT_LABEL_UNKNOWN,
    MODEL_ASSESSMENT_STATUS_COMPLETED,
    MODEL_ASSESSMENT_STATUS_FAILED,
    MODEL_ASSESSMENT_STATUS_INCONCLUSIVE,
    MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED,
    ModelAssessment,
)
from application.models.scope_assessment import (
    SCOPE_FAMILY_OUT_OF_SCOPE,
    assess_email_scope,
)
from application.ports.outbound.model_assessment import AssessRawEmailWithModelCommand
from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


_DEFAULT_MODEL_NAME = "phishshield_baseline_candidate"
_DEFAULT_FEATURE_SET = "text_with_light_metadata"
_SIGNAL_EXPERIMENTAL = "Experimental sklearn baseline."
_SIGNAL_FEATURES = "Uses text_with_light_metadata features."
_SIGNAL_DETERMINISTIC = "Deterministic analysis remains authoritative."
_HIGH_CONFIDENCE_THRESHOLD = 0.85
_SIGNAL_SCOPE = "Deterministic scope gate."


class SklearnModelAssessmentAdapter:
    def __init__(
        self,
        model_artifact_path: Path,
        metadata_path: Path,
        email_content_extractor: PythonEmailContentExtractorAdapter | None = None,
    ) -> None:
        self._model_artifact_path = model_artifact_path
        self._metadata_path = metadata_path
        self._email_content_extractor = email_content_extractor or PythonEmailContentExtractorAdapter()
        self._model: Any | None = None
        self._metadata: dict[str, Any] | None = None

    def assess_raw_email(
        self,
        command: AssessRawEmailWithModelCommand,
    ) -> ModelAssessment:
        if not self._model_artifact_path.is_file() or not self._metadata_path.is_file():
            return _not_configured_assessment()

        try:
            model = self._load_model()
            metadata = self._load_metadata()
            extracted_email = self._email_content_extractor.extract(command.raw_email)
            scope = assess_email_scope(extracted_email)
            if scope.family == SCOPE_FAMILY_OUT_OF_SCOPE:
                return _out_of_scope_assessment(scope.reason)
            feature_text = _extracted_email_to_feature_text(extracted_email)
            label, confidence = _predict_label_and_confidence(model, feature_text)
        except Exception as exc:
            return _failed_assessment(str(exc))

        return ModelAssessment(
            status=MODEL_ASSESSMENT_STATUS_INCONCLUSIVE if label == MODEL_ASSESSMENT_LABEL_INCONCLUSIVE else MODEL_ASSESSMENT_STATUS_COMPLETED,
            label=label,
            confidence=confidence,
            summary=_summary_for_label(label=label, confidence=confidence),
            signals=(
                _SIGNAL_EXPERIMENTAL,
                _SIGNAL_FEATURES,
                f"Scope family: {scope.family}.",
                _SIGNAL_SCOPE,
                _SIGNAL_DETERMINISTIC,
            ),
            model_name=str(metadata.get("model_name") or _DEFAULT_MODEL_NAME),
            model_version=_model_version(metadata),
            error_message="",
        )

    def _load_model(self):
        if self._model is None:
            self._model = joblib.load(self._model_artifact_path)

        return self._model

    def _load_metadata(self) -> dict[str, Any]:
        if self._metadata is None:
            metadata = json.loads(self._metadata_path.read_text(encoding="utf-8"))
            if metadata.get("feature_set") != _DEFAULT_FEATURE_SET:
                raise ValueError("Unsupported model feature set")
            self._metadata = metadata

        return self._metadata


def _not_configured_assessment() -> ModelAssessment:
    return ModelAssessment(
        status=MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED,
        label=MODEL_ASSESSMENT_LABEL_UNKNOWN,
        confidence=None,
        summary="",
        signals=(),
        model_name="",
        model_version="",
        error_message="",
    )


def _failed_assessment(error_message: str) -> ModelAssessment:
    return ModelAssessment(
        status=MODEL_ASSESSMENT_STATUS_FAILED,
        label=MODEL_ASSESSMENT_LABEL_UNKNOWN,
        confidence=None,
        summary="Model assessment failed before producing an advisory result.",
        signals=(),
        model_name="",
        model_version="",
        error_message=error_message,
    )


def _out_of_scope_assessment(reason: str) -> ModelAssessment:
    return ModelAssessment(
        status=MODEL_ASSESSMENT_STATUS_INCONCLUSIVE,
        label=MODEL_ASSESSMENT_LABEL_INCONCLUSIVE,
        confidence=None,
        summary="The deterministic scope gate could not place this email in a validated advisory family.",
        signals=(f"Scope gate reason: {reason}.", _SIGNAL_DETERMINISTIC),
        model_name="",
        model_version="",
        error_message="",
    )


def _extracted_email_to_feature_text(extracted_email: ExtractedEmailContent) -> str:
    text_parts = [extracted_email.subject, extracted_email.body_text]
    text_parts.extend(extracted_email.urls)
    text_parts.extend(extracted_email.attachment_filenames)

    return "\n".join(text_parts)


def _predict_label_and_confidence(model, feature_text: str) -> tuple[str, float]:
    probabilities = model.predict_proba([feature_text])[0]
    classes = list(model.named_steps["classifier"].classes_)
    suspicious_index = classes.index(MODEL_ASSESSMENT_LABEL_SUSPICIOUS)
    suspicious_probability = float(probabilities[suspicious_index])

    confidence = max(suspicious_probability, 1.0 - suspicious_probability)
    if (1.0 - _HIGH_CONFIDENCE_THRESHOLD) < suspicious_probability < _HIGH_CONFIDENCE_THRESHOLD:
        return MODEL_ASSESSMENT_LABEL_INCONCLUSIVE, confidence

    if suspicious_probability >= _HIGH_CONFIDENCE_THRESHOLD:
        return MODEL_ASSESSMENT_LABEL_SUSPICIOUS, suspicious_probability

    if suspicious_probability <= (1.0 - _HIGH_CONFIDENCE_THRESHOLD):
        return MODEL_ASSESSMENT_LABEL_BENIGN, 1.0 - suspicious_probability

    return MODEL_ASSESSMENT_LABEL_INCONCLUSIVE, confidence


def _summary_for_label(label: str, confidence: float) -> str:
    if label == MODEL_ASSESSMENT_LABEL_INCONCLUSIVE:
        return f"The model assessment is inconclusive at confidence {confidence:.2f}; review deterministic findings and evidence."

    if label == MODEL_ASSESSMENT_LABEL_SUSPICIOUS:
        return f"Experimental model assessment suggests suspicious email characteristics with confidence {confidence:.2f}."

    return f"Experimental model assessment suggests benign email characteristics with confidence {confidence:.2f}."


def _model_version(metadata: dict[str, Any]) -> str:
    git_commit = str(metadata.get("git_commit") or "")
    if git_commit:
        return git_commit

    return str(metadata.get("created_at") or "")
