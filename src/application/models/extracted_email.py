from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedEmailContent:
    sender_domain: str
    urls: tuple[str, ...]
    attachment_filenames: tuple[str, ...]
    subject: str
    body_text: str
    spf_result: str
    dkim_result: str
    dmarc_result: str
