from typing import Protocol

from application.models.extracted_email import ExtractedEmailContent


class EmailContentExtractorPort(Protocol):
    def extract(self, email_bytes: bytes) -> ExtractedEmailContent:
        """Extract normalized email content from raw email bytes."""
