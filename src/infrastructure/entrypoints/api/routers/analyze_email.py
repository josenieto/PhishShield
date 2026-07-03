from fastapi import APIRouter, File, UploadFile

from application.use_cases.analyze_raw_email import (
    AnalyzeRawEmailCommand,
    AnalyzeRawEmailUseCase,
)
from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)
from infrastructure.entrypoints.api.schemas.analyze_email import (
    AnalyzeEmailResponse,
    extracted_email_analysis_to_response,
)


router = APIRouter()


@router.post("/analyze-email", response_model=AnalyzeEmailResponse)
async def analyze_email(file: UploadFile = File(...)) -> AnalyzeEmailResponse:
    email_bytes = await file.read()
    use_case = AnalyzeRawEmailUseCase(
        email_content_extractor=PythonEmailContentExtractorAdapter()
    )
    analysis = use_case.execute(
        AnalyzeRawEmailCommand(
            email_bytes=email_bytes,
            suspicious_tlds=_default_suspicious_tlds(),
            allowed_url_schemes=_default_allowed_url_schemes(),
            known_shorteners=_default_known_shorteners(),
            urgency_terms=_default_urgency_terms(),
            financial_pressure_terms=_default_financial_pressure_terms(),
            credential_request_terms=_default_credential_request_terms(),
            finding_weights=_default_finding_weights(),
            critical_indicators=_default_critical_indicators(),
        )
    )

    return extracted_email_analysis_to_response(analysis)


def _default_suspicious_tlds() -> set[str]:
    return {"mov", "top", "xyz", "zip"}


def _default_allowed_url_schemes() -> set[str]:
    return {"http", "https"}


def _default_known_shorteners() -> set[str]:
    return {"bit.ly", "t.co", "tinyurl.com"}


def _default_urgency_terms() -> set[str]:
    return {"act now", "immediately", "urgent"}


def _default_financial_pressure_terms() -> set[str]:
    return {"account locked", "invoice overdue", "payment required"}


def _default_credential_request_terms() -> set[str]:
    return {"confirm your login", "password", "verify your account"}


def _default_finding_weights() -> dict[str, int]:
    return {
        "DOMAIN_CONTAINS_PUNYCODE": 30,
        "DOMAIN_HAS_MIXED_SCRIPTS": 30,
        "DOMAIN_HAS_CONFUSABLE_CHARACTERS": 30,
        "DOMAIN_HAS_SUSPICIOUS_DEPTH": 15,
        "DOMAIN_LOOKS_LIKE_IP_ADDRESS": 15,
        "DOMAIN_HAS_SUSPICIOUS_TLD": 20,
        "URL_SCHEME_NOT_ALLOWED": 15,
        "URL_HAS_SUSPICIOUS_SCHEME": 30,
        "URL_HAS_EMBEDDED_CREDENTIALS": 25,
        "URL_HAS_SUSPICIOUS_QUERY_DENSITY": 15,
        "URL_USES_KNOWN_SHORTENER_DOMAIN": 15,
        "ATTACHMENT_HAS_EXECUTABLE_EXTENSION": 40,
        "ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION": 15,
        "ATTACHMENT_HAS_DOUBLE_EXTENSION": 30,
        "ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS": 30,
        "AUTHENTICATION_SPF_FAILED": 25,
        "AUTHENTICATION_DKIM_FAILED": 25,
        "AUTHENTICATION_DMARC_FAILED": 50,
        "AUTHENTICATION_HAS_MULTIPLE_FAILURES": 50,
        "AUTHENTICATION_RESULTS_UNKNOWN": 15,
        "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS": 10,
        "SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS": 15,
        "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS": 25,
    }


def _default_critical_indicators() -> set[str]:
    return {
        "ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
        "AUTHENTICATION_DMARC_FAILED",
        "AUTHENTICATION_HAS_MULTIPLE_FAILURES",
    }
