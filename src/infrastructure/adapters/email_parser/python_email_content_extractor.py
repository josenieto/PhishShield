from email import policy
from email.message import EmailMessage, Message
from email.parser import BytesParser
from email.utils import parseaddr

from application.models.extracted_email import ExtractedEmailContent


class PythonEmailContentExtractorAdapter:
    def extract(self, email_bytes: bytes) -> ExtractedEmailContent:
        """Extract normalized email content using Python's standard email parser."""
        message = BytesParser(policy=policy.default).parsebytes(email_bytes)

        return ExtractedEmailContent(
            sender_domain=_extract_sender_domain(message),
            urls=(),
            attachment_filenames=_extract_attachment_filenames(message),
            subject=str(message.get("Subject", "")),
            body_text=_extract_plain_text_body(message),
            spf_result="unknown",
            dkim_result="unknown",
            dmarc_result="unknown",
        )


def _extract_sender_domain(message: Message) -> str:
    sender_header = message.get("From", "")
    _, sender_email = parseaddr(str(sender_header))

    if "@" not in sender_email:
        return ""

    return sender_email.rsplit("@", maxsplit=1)[1].lower()


def _extract_attachment_filenames(message: Message) -> tuple[str, ...]:
    return tuple(
        filename
        for part in message.walk()
        if (filename := part.get_filename())
    )


def _extract_plain_text_body(message: Message) -> str:
    if message.is_multipart():
        body_parts = [
            _decode_text_part(part)
            for part in message.walk()
            if _is_plain_text_body_part(part)
        ]

        return "\n".join(body_part for body_part in body_parts if body_part)

    if _is_plain_text_body_part(message):
        return _decode_text_part(message)

    return ""


def _is_plain_text_body_part(part: Message) -> bool:
    return (
        part.get_content_type() == "text/plain"
        and part.get_content_disposition() != "attachment"
    )


def _decode_text_part(part: Message) -> str:
    if isinstance(part, EmailMessage):
        content = part.get_content()
        if isinstance(content, str):
            return content.strip()

    payload = part.get_payload(decode=True)
    if not isinstance(payload, bytes):
        return ""

    charset = part.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace").strip()
