from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from application.use_cases.assess_raw_email_with_model import (
    AssessRawEmailWithModelUseCase,
    AssessRawEmailWithModelUseCaseCommand,
)
from infrastructure.adapters.model_assessment.noop_model_assessment_adapter import (
    NoopModelAssessmentAdapter,
)
from infrastructure.config.api_defaults import DEFAULT_API_SETTINGS, ApiSettings
from infrastructure.entrypoints.api.routers.analyze_email import _read_upload_file_with_limit
from infrastructure.entrypoints.api.schemas.model_assessment import (
    AnalyzeEmailModelAssessmentResponse,
    model_assessment_result_to_response,
)


router = APIRouter()


@router.post(
    "/analyze-email-model-assessment",
    response_model=AnalyzeEmailModelAssessmentResponse,
)
async def analyze_email_model_assessment(
    request: Request,
    file: UploadFile = File(...),
) -> AnalyzeEmailModelAssessmentResponse:
    api_settings = getattr(request.app.state, "api_settings", DEFAULT_API_SETTINGS)
    email_bytes = await _read_upload_file_with_limit(
        file,
        max_bytes=api_settings.max_upload_bytes,
    )

    try:
        assessment = _build_assess_raw_email_with_model_use_case(api_settings).execute(
            AssessRawEmailWithModelUseCaseCommand(
                raw_email=email_bytes,
                filename=file.filename or "uploaded-email.eml",
                content_type=file.content_type or "message/rfc822",
                max_input_bytes=api_settings.max_upload_bytes,
            )
        )
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Uploaded email could not be assessed by the model.",
        ) from None

    return model_assessment_result_to_response(assessment)


def _build_assess_raw_email_with_model_use_case(api_settings: ApiSettings) -> AssessRawEmailWithModelUseCase:
    if api_settings.model_assessment_enabled:
        from infrastructure.adapters.model_assessment.sklearn_model_assessment_adapter import (
            SklearnModelAssessmentAdapter,
        )

        return AssessRawEmailWithModelUseCase(
            model_assessment_port=SklearnModelAssessmentAdapter(
                model_artifact_path=Path(api_settings.model_artifact_path),
                metadata_path=Path(api_settings.model_metadata_path),
            )
        )

    return AssessRawEmailWithModelUseCase(
        model_assessment_port=NoopModelAssessmentAdapter()
    )
