from application.models.extracted_email import ExtractedEmailContent
from application.ports.outbound.email_content_extractor import EmailContentExtractorPort


class FakeEmailContentExtractor:
    def extract(self, email_bytes: bytes) -> ExtractedEmailContent:
        return ExtractedEmailContent(
            sender_domain="example.com",
            urls=("https://example.com/login",),
            attachment_filenames=("invoice.pdf",),
            subject="Invoice available",
            body_text="Please review the attached invoice.",
            spf_result="pass",
            dkim_result="none",
            dmarc_result="pass",
        )


def test_should_use_email_content_extractor_port_contract() -> None:
    extractor: EmailContentExtractorPort = FakeEmailContentExtractor()

    extracted_email = extractor.extract(b"raw email bytes")

    assert extracted_email == ExtractedEmailContent(
        sender_domain="example.com",
        urls=("https://example.com/login",),
        attachment_filenames=("invoice.pdf",),
        subject="Invoice available",
        body_text="Please review the attached invoice.",
        spf_result="pass",
        dkim_result="none",
        dmarc_result="pass",
    )
