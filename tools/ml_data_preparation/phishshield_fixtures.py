import hashlib

from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)
from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample


PHISHSHIELD_FIXTURE_SOURCE = "phishshield-fixtures"
PHISHSHIELD_FIXTURE_SOURCE_URI = "tests/fixtures/emails"

NORMALIZED_LABEL_BENIGN = "benign"
NORMALIZED_LABEL_SUSPICIOUS = "suspicious"

_ALLOWED_LABELS = {NORMALIZED_LABEL_BENIGN, NORMALIZED_LABEL_SUSPICIOUS}


def prepare_phishshield_fixture_email(
    raw_email: bytes,
    source_id: str,
    normalized_label: str,
    source_uri: str = PHISHSHIELD_FIXTURE_SOURCE_URI,
) -> PreparedEmailSample:
    if normalized_label not in _ALLOWED_LABELS:
        raise ValueError(f"Unsupported PhishShield fixture label: {normalized_label}")

    extracted_email = PythonEmailContentExtractorAdapter().extract(raw_email)
    sample_id = _build_sample_id(
        source=PHISHSHIELD_FIXTURE_SOURCE,
        source_id=source_id,
        normalized_label=normalized_label,
        subject=extracted_email.subject,
        body_text=extracted_email.body_text,
        urls=extracted_email.urls,
        attachment_filenames=extracted_email.attachment_filenames,
    )

    return PreparedEmailSample(
        sample_id=sample_id,
        source=PHISHSHIELD_FIXTURE_SOURCE,
        source_id=source_id,
        source_uri=source_uri,
        original_label=normalized_label,
        normalized_label=normalized_label,
        subject=extracted_email.subject,
        body_text=extracted_email.body_text,
        sender_domain=extracted_email.sender_domain,
        urls=extracted_email.urls,
        attachment_filenames=extracted_email.attachment_filenames,
        raw_available=True,
        metadata={"fixture_name": source_id},
    )


def _build_sample_id(
    source: str,
    source_id: str,
    normalized_label: str,
    subject: str,
    body_text: str,
    urls: tuple[str, ...],
    attachment_filenames: tuple[str, ...],
) -> str:
    hash_input = "\n".join(
        (
            source,
            source_id,
            normalized_label,
            subject,
            body_text,
            "\n".join(urls),
            "\n".join(attachment_filenames),
        )
    )

    return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
