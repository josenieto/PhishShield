from application.models.model_assessment import (
    MODEL_ASSESSMENT_LABEL_UNKNOWN,
    MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED,
    ModelAssessment,
)
from infrastructure.entrypoints.api.schemas.model_assessment import (
    AnalyzeEmailModelAssessmentResponse,
    ModelAssessmentResponse,
    model_assessment_result_to_response,
    model_assessment_to_response,
)


def test_should_convert_model_assessment_to_response() -> None:
    assessment = ModelAssessment(
        status=MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED,
        label=MODEL_ASSESSMENT_LABEL_UNKNOWN,
        confidence=None,
        summary="",
        signals=(),
        model_name="",
        model_version="",
        abstention_reason=None,
        error_message="",
    )

    assert model_assessment_to_response(assessment) == ModelAssessmentResponse(
        status=MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED,
        label=MODEL_ASSESSMENT_LABEL_UNKNOWN,
        confidence=None,
        summary="",
        signals=[],
        model_name="",
        model_version="",
        abstention_reason=None,
        error_message="",
    )


def test_should_wrap_model_assessment_result_response() -> None:
    assessment = ModelAssessment(
        status=MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED,
        label=MODEL_ASSESSMENT_LABEL_UNKNOWN,
        confidence=None,
        summary="",
        signals=(),
        model_name="",
        model_version="",
        abstention_reason=None,
        error_message="",
    )

    assert model_assessment_result_to_response(assessment) == AnalyzeEmailModelAssessmentResponse(
        model_assessment=ModelAssessmentResponse(
            status=MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED,
            label=MODEL_ASSESSMENT_LABEL_UNKNOWN,
            confidence=None,
            summary="",
            signals=[],
                model_name="",
                model_version="",
                abstention_reason=None,
                error_message="",
        )
    )
