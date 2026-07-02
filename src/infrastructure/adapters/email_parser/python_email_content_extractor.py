import re

from email import policy
from email.header import decode_header, make_header
from email.message import EmailMessage, Message
from email.parser import BytesParser
from email.utils import parseaddr

from application.models.extracted_email import ExtractedEmailContent


_HTTP_URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
_AUTHENTICATION_RESULT_PATTERN_TEMPLATE = r"\b{mechanism}=([a-zA-Z]+)"
_TRAILING_URL_PUNCTUATION = ".,;:!?) ]"


class PythonEmailContentExtractorAdapter:
    def extract(self, email_bytes: bytes) -> ExtractedEmailContent:
        """Extract normalized email content using Python's standard email parser."""
        message = BytesParser(policy=policy.default).parsebytes(email_bytes)

        body_text = _extract_plain_text_body(message)
        spf_result, dkim_result, dmarc_result = _extract_authentication_results(message)

        return ExtractedEmailContent(
            sender_domain=_extract_sender_domain(message),
            urls=_extract_urls_from_text(body_text),
            attachment_filenames=_extract_attachment_filenames(message),
            subject=_decode_header_value(message.get("Subject", "")),
            body_text=body_text,
            spf_result=spf_result,
            dkim_result=dkim_result,
            dmarc_result=dmarc_result,
        )


def _extract_sender_domain(message: Message) -> str:
    sender_header = message.get("From", "")
    _, sender_email = parseaddr(str(sender_header))

    if "@" not in sender_email:
        return ""

    return sender_email.rsplit("@", maxsplit=1)[1].lower()


def _decode_header_value(value: object) -> str:
    if not value:
        return ""

    return str(make_header(decode_header(str(value))))


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


def _extract_urls_from_text(text: str) -> tuple[str, ...]:
    return tuple(
        match.group(0).rstrip(_TRAILING_URL_PUNCTUATION)
        for match in _HTTP_URL_PATTERN.finditer(text)
    )


def _extract_authentication_results(message: Message) -> tuple[str, str, str]:
    authentication_results = "\n".join(
        str(header_value)
        for header_value in message.get_all("Authentication-Results", [])
    )

    return (
        _extract_authentication_result(authentication_results, "spf"),
        _extract_authentication_result(authentication_results, "dkim"),
        _extract_authentication_result(authentication_results, "dmarc"),
    )


def _extract_authentication_result(header_value: str, mechanism: str) -> str:
    result_match = re.search(
        _AUTHENTICATION_RESULT_PATTERN_TEMPLATE.format(mechanism=mechanism),
        header_value,
        re.IGNORECASE,
    )

    if result_match is None:
        return "unknown"

    return result_match.group(1).lower()


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
