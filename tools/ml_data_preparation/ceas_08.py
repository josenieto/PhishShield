import hashlib
import re
from email.utils import parseaddr

from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample


CEAS_08_SOURCE = "ceas_08"
CEAS_08_SOURCE_URI = "https://doi.org/10.5281/zenodo.8339691"
NORMALIZED_LABEL_BENIGN = "benign"
NORMALIZED_LABEL_SUSPICIOUS = "suspicious"
_URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
_TRAILING_URL_PUNCTUATION = ".,;:!?) ]"


def normalize_ceas_label(original_label: str, label_map: dict[str, str]) -> str:
    normalized = original_label.strip()
    mapped = label_map.get(normalized)
    if mapped not in {NORMALIZED_LABEL_BENIGN, NORMALIZED_LABEL_SUSPICIOUS}:
        raise ValueError(f"Unsupported CEAS-08 label mapping: {original_label}")
    return mapped


def prepare_ceas_08_row(
    row: dict[str, str],
    row_number: int,
    label_map: dict[str, str],
    source_uri: str = CEAS_08_SOURCE_URI,
) -> PreparedEmailSample:
    original_label = str(row.get("label") or "")
    normalized_label = normalize_ceas_label(original_label, label_map)
    subject = str(row.get("subject") or "").strip()
    body_text = str(row.get("body") or "").strip()
    urls = _extract_urls(body_text)
    source_id = f"row-{row_number}"

    return PreparedEmailSample(
        sample_id=_sample_id(subject, body_text, urls, source_id),
        source=CEAS_08_SOURCE,
        source_id=source_id,
        source_uri=source_uri,
        original_label=original_label,
        normalized_label=normalized_label,
        subject=subject,
        body_text=body_text,
        sender_domain=_sender_domain(row.get("sender", "")),
        urls=urls,
        attachment_filenames=(),
        raw_available=False,
        metadata={
            "ceas_row_number": str(row_number),
            "receiver": str(row.get("receiver") or ""),
            "date": str(row.get("date") or ""),
            "source_urls_flag": str(row.get("urls") or ""),
        },
    )


def _extract_urls(text: str) -> tuple[str, ...]:
    return tuple(
        match.group(0).rstrip(_TRAILING_URL_PUNCTUATION)
        for match in _URL_PATTERN.finditer(text)
    )


def _sender_domain(sender: str) -> str:
    _, address = parseaddr(sender)
    return address.rsplit("@", maxsplit=1)[1].lower() if "@" in address else ""


def _sample_id(subject: str, body: str, urls: tuple[str, ...], source_id: str) -> str:
    content = "\n".join((CEAS_08_SOURCE, source_id, subject, body, "\n".join(urls)))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
