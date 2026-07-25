import hashlib
import re

from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)

from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample


FRAUDULENT_EMAIL_CORPUS_SOURCE = "fraudulent_email_corpus"
FRAUDULENT_EMAIL_CORPUS_SOURCE_URI = "https://www.kaggle.com/datasets/rtatman/fraudulent-email-corpus"
FRAUDULENT_EMAIL_CORPUS_ORIGINAL_LABEL = "fraud"
NORMALIZED_LABEL_SUSPICIOUS = "suspicious"

_MESSAGE_BOUNDARY_PATTERN = re.compile(r"(?m)^(?:From r\s+.*\n)?Return-Path:")
_MESSAGE_BOUNDARY_BYTES_PATTERN = re.compile(rb"(?m)^(?:From r\s+.*\n)?Return-Path:")


def split_fraudulent_email_corpus_messages(corpus_text: str) -> tuple[str, ...]:
    normalized_text = corpus_text.replace("\r\n", "\n").replace("\r", "\n")
    starts = [match.start() for match in _MESSAGE_BOUNDARY_PATTERN.finditer(normalized_text)]

    if not starts:
        return ()

    messages: list[str] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(normalized_text)
        message = normalized_text[start:end].strip()
        if message:
            messages.append(_remove_mbox_from_line(message))

    return tuple(messages)


def split_fraudulent_email_corpus_message_bytes(corpus_bytes: bytes) -> tuple[bytes, ...]:
    normalized_bytes = corpus_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    starts = [match.start() for match in _MESSAGE_BOUNDARY_BYTES_PATTERN.finditer(normalized_bytes)]

    if not starts:
        return ()

    messages: list[bytes] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(normalized_bytes)
        message = normalized_bytes[start:end].strip()
        if message:
            messages.append(_remove_mbox_from_line_bytes(message))

    return tuple(messages)


def prepare_fraudulent_email_corpus_message(
    raw_message: bytes | str,
    source_id: str,
    source_uri: str = FRAUDULENT_EMAIL_CORPUS_SOURCE_URI,
) -> PreparedEmailSample:
    message_bytes = raw_message if isinstance(raw_message, bytes) else raw_message.encode("utf-8", errors="replace")
    extracted_email = PythonEmailContentExtractorAdapter().extract(message_bytes)
    sample_id = _build_sample_id(
        source=FRAUDULENT_EMAIL_CORPUS_SOURCE,
        source_id=source_id,
        normalized_label=NORMALIZED_LABEL_SUSPICIOUS,
        subject=extracted_email.subject,
        body_text=extracted_email.body_text,
        urls=extracted_email.urls,
        attachment_filenames=extracted_email.attachment_filenames,
    )

    return PreparedEmailSample(
        sample_id=sample_id,
        source=FRAUDULENT_EMAIL_CORPUS_SOURCE,
        source_id=source_id,
        source_uri=source_uri,
        original_label=FRAUDULENT_EMAIL_CORPUS_ORIGINAL_LABEL,
        normalized_label=NORMALIZED_LABEL_SUSPICIOUS,
        subject=extracted_email.subject,
        body_text=extracted_email.body_text,
        sender_domain=extracted_email.sender_domain,
        urls=extracted_email.urls,
        attachment_filenames=extracted_email.attachment_filenames,
        raw_available=True,
        metadata={"original_label": FRAUDULENT_EMAIL_CORPUS_ORIGINAL_LABEL},
    )


def _remove_mbox_from_line(message: str) -> str:
    lines = message.split("\n")
    if lines and lines[0].startswith("From r "):
        return "\n".join(lines[1:]).strip()

    return message


def _remove_mbox_from_line_bytes(message: bytes) -> bytes:
    lines = message.split(b"\n")
    if lines and lines[0].startswith(b"From r "):
        return b"\n".join(lines[1:]).strip()

    return message


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
