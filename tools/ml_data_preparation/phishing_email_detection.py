import hashlib
import re

from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample


PHISHING_EMAIL_DETECTION_SOURCE = "phishing_email_detection"
PHISHING_EMAIL_DETECTION_SOURCE_URI = "https://www.kaggle.com/datasets/subhajournal/phishingemails"
NORMALIZED_LABEL_BENIGN = "benign"
NORMALIZED_LABEL_SUSPICIOUS = "suspicious"

_LABEL_MAPPING = {
    "Safe Email": NORMALIZED_LABEL_BENIGN,
    "Phishing Email": NORMALIZED_LABEL_SUSPICIOUS,
}
_HTTP_URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
_TRAILING_URL_PUNCTUATION = ".,;:!?) ]"


def normalize_phishing_email_detection_label(original_label: str) -> str:
    normalized_source_label = original_label.strip()

    if normalized_source_label not in _LABEL_MAPPING:
        raise ValueError(f"Unsupported Phishing Email Detection label: {original_label}")

    return _LABEL_MAPPING[normalized_source_label]


def prepare_phishing_email_detection_row(
    email_text: str,
    source_id: str,
    original_label: str,
    csv_row_number: int,
    source_uri: str = PHISHING_EMAIL_DETECTION_SOURCE_URI,
) -> PreparedEmailSample:
    body_text = email_text.strip()
    normalized_label = normalize_phishing_email_detection_label(original_label)
    urls = _extract_urls_from_text(body_text)
    sample_id = _build_sample_id(
        source=PHISHING_EMAIL_DETECTION_SOURCE,
        source_id=source_id,
        normalized_label=normalized_label,
        body_text=body_text,
        urls=urls,
    )

    return PreparedEmailSample(
        sample_id=sample_id,
        source=PHISHING_EMAIL_DETECTION_SOURCE,
        source_id=source_id,
        source_uri=source_uri,
        original_label=original_label,
        normalized_label=normalized_label,
        subject="",
        body_text=body_text,
        sender_domain="",
        urls=urls,
        attachment_filenames=(),
        raw_available=False,
        metadata={
            "original_label": original_label,
            "csv_row_number": str(csv_row_number),
        },
    )


def _extract_urls_from_text(text: str) -> tuple[str, ...]:
    return tuple(
        match.group(0).rstrip(_TRAILING_URL_PUNCTUATION)
        for match in _HTTP_URL_PATTERN.finditer(text)
    )


def _build_sample_id(
    source: str,
    source_id: str,
    normalized_label: str,
    body_text: str,
    urls: tuple[str, ...],
) -> str:
    hash_input = "\n".join(
        (
            source,
            source_id,
            normalized_label,
            body_text,
            "\n".join(urls),
        )
    )

    return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
