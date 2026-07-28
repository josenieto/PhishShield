import hashlib
from pathlib import Path, PurePosixPath

from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)
from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample


ENRON_SOURCE = "enron"
ENRON_SOURCE_URI = "https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz"
ENRON_ORIGINAL_LABEL = "benign"
NORMALIZED_LABEL_BENIGN = "benign"


def prepare_enron_email(
    raw_email: bytes,
    source_id: str,
    relative_path: str,
    source_uri: str = ENRON_SOURCE_URI,
) -> PreparedEmailSample:
    extracted_email = PythonEmailContentExtractorAdapter().extract(raw_email)
    mailbox_user, folder = parse_enron_relative_path(relative_path)
    sample_id = _build_sample_id(
        source=ENRON_SOURCE,
        source_id=source_id,
        normalized_label=NORMALIZED_LABEL_BENIGN,
        subject=extracted_email.subject,
        body_text=extracted_email.body_text,
        urls=extracted_email.urls,
        attachment_filenames=extracted_email.attachment_filenames,
    )

    return PreparedEmailSample(
        sample_id=sample_id,
        source=ENRON_SOURCE,
        source_id=source_id,
        source_uri=source_uri,
        original_label=ENRON_ORIGINAL_LABEL,
        normalized_label=NORMALIZED_LABEL_BENIGN,
        subject=extracted_email.subject,
        body_text=extracted_email.body_text,
        sender_domain=extracted_email.sender_domain,
        urls=extracted_email.urls,
        attachment_filenames=extracted_email.attachment_filenames,
        raw_available=True,
        metadata={
            "relative_path": relative_path,
            "mailbox_user": mailbox_user,
            "folder": folder,
            "original_label": ENRON_ORIGINAL_LABEL,
        },
    )


def parse_enron_relative_path(relative_path: str) -> tuple[str, str]:
    path = PurePosixPath(relative_path.replace("\\", "/"))
    parts = path.parts

    if len(parts) < 3:
        return "", ""

    if parts[0] == "maildir":
        parts = parts[1:]

    mailbox_user = parts[0]
    folder = "/".join(parts[1:-1])

    return mailbox_user, folder


def enron_source_id_from_path(input_dir: Path, email_path: Path) -> str:
    return email_path.relative_to(input_dir).as_posix()


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
