import hashlib

from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)

from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample


SPAMASSASSIN_SOURCE = "spamassassin"
SPAMASSASSIN_SOURCE_URI = "https://spamassassin.apache.org/old/publiccorpus/"

NORMALIZED_LABEL_BENIGN = "benign"
NORMALIZED_LABEL_SUSPICIOUS = "suspicious"

_SPAMASSASSIN_LABEL_MAPPING = {
    "easy_ham": NORMALIZED_LABEL_BENIGN,
    "hard_ham": NORMALIZED_LABEL_BENIGN,
    "ham": NORMALIZED_LABEL_BENIGN,
    "spam": NORMALIZED_LABEL_SUSPICIOUS,
}


def normalize_spamassassin_label(original_label: str) -> str:
    normalized_source_label = original_label.strip().lower()

    if normalized_source_label not in _SPAMASSASSIN_LABEL_MAPPING:
        raise ValueError(f"Unsupported SpamAssassin label: {original_label}")

    return _SPAMASSASSIN_LABEL_MAPPING[normalized_source_label]


def prepare_spamassassin_email(
    raw_email: bytes,
    source_id: str,
    original_label: str,
    source_uri: str = SPAMASSASSIN_SOURCE_URI,
) -> PreparedEmailSample:
    normalized_label = normalize_spamassassin_label(original_label)
    extracted_email = PythonEmailContentExtractorAdapter().extract(raw_email)
    sample_id = _build_sample_id(
        source=SPAMASSASSIN_SOURCE,
        source_id=source_id,
        normalized_label=normalized_label,
        subject=extracted_email.subject,
        body_text=extracted_email.body_text,
        urls=extracted_email.urls,
        attachment_filenames=extracted_email.attachment_filenames,
    )

    return PreparedEmailSample(
        sample_id=sample_id,
        source=SPAMASSASSIN_SOURCE,
        source_id=source_id,
        source_uri=source_uri,
        original_label=original_label,
        normalized_label=normalized_label,
        subject=extracted_email.subject,
        body_text=extracted_email.body_text,
        sender_domain=extracted_email.sender_domain,
        urls=extracted_email.urls,
        attachment_filenames=extracted_email.attachment_filenames,
        raw_available=True,
        metadata={"original_label": original_label},
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
