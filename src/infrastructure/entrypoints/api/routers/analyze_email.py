from fastapi import APIRouter, File, HTTPException, UploadFile

from application.use_cases.analyze_raw_email import (
    AnalyzeRawEmailCommand,
    AnalyzeRawEmailUseCase,
)
from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)
from infrastructure.config.api_defaults import DEFAULT_API_SETTINGS
from infrastructure.config.analysis_defaults import (
    DEFAULT_ALLOWED_URL_SCHEMES,
    DEFAULT_CREDENTIAL_REQUEST_TERMS,
    DEFAULT_CRITICAL_INDICATORS,
    DEFAULT_FINDING_WEIGHTS,
    DEFAULT_FINANCIAL_PRESSURE_TERMS,
    DEFAULT_KNOWN_SHORTENERS,
    DEFAULT_SUSPICIOUS_TLDS,
    DEFAULT_URGENCY_TERMS,
)
from infrastructure.entrypoints.api.schemas.analyze_email import (
    AnalyzeEmailResponse,
    extracted_email_analysis_to_response,
)


router = APIRouter()


@router.post("/analyze-email", response_model=AnalyzeEmailResponse)
async def analyze_email(file: UploadFile = File(...)) -> AnalyzeEmailResponse:
    email_bytes = await _read_upload_file_with_limit(file)
    try:
        analysis = _build_analyze_raw_email_use_case().execute(
            AnalyzeRawEmailCommand(
                email_bytes=email_bytes,
                suspicious_tlds=DEFAULT_SUSPICIOUS_TLDS,
                allowed_url_schemes=DEFAULT_ALLOWED_URL_SCHEMES,
                known_shorteners=DEFAULT_KNOWN_SHORTENERS,
                urgency_terms=DEFAULT_URGENCY_TERMS,
                financial_pressure_terms=DEFAULT_FINANCIAL_PRESSURE_TERMS,
                credential_request_terms=DEFAULT_CREDENTIAL_REQUEST_TERMS,
                finding_weights=DEFAULT_FINDING_WEIGHTS,
                critical_indicators=DEFAULT_CRITICAL_INDICATORS,
            )
        )
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Uploaded email could not be analyzed.",
        ) from None

    return extracted_email_analysis_to_response(analysis)


def _build_analyze_raw_email_use_case() -> AnalyzeRawEmailUseCase:
    return AnalyzeRawEmailUseCase(
        email_content_extractor=PythonEmailContentExtractorAdapter()
    )


async def _read_upload_file_with_limit(
    file: UploadFile,
    max_bytes: int = DEFAULT_API_SETTINGS.max_upload_bytes,
) -> bytes:
    email_bytes = await file.read(max_bytes + 1)

    if len(email_bytes) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail="Uploaded email exceeds maximum allowed size.",
        )

    return email_bytes
