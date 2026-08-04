from pydantic import BaseModel

from application.models.model_assessment import ModelAssessment


class ModelAssessmentResponse(BaseModel):
    status: str
    label: str
    confidence: float | None
    summary: str
    signals: list[str]
    model_name: str
    model_version: str
    abstention_reason: str | None
    error_message: str


class AnalyzeEmailModelAssessmentResponse(BaseModel):
    model_assessment: ModelAssessmentResponse


def model_assessment_to_response(
    assessment: ModelAssessment,
) -> ModelAssessmentResponse:
    return ModelAssessmentResponse(
        status=assessment.status,
        label=assessment.label,
        confidence=assessment.confidence,
        summary=assessment.summary,
        signals=list(assessment.signals),
        model_name=assessment.model_name,
        model_version=assessment.model_version,
        abstention_reason=assessment.abstention_reason,
        error_message=assessment.error_message,
    )


def model_assessment_result_to_response(
    assessment: ModelAssessment,
) -> AnalyzeEmailModelAssessmentResponse:
    return AnalyzeEmailModelAssessmentResponse(
        model_assessment=model_assessment_to_response(assessment)
    )
