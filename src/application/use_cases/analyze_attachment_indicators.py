from dataclasses import dataclass

from domain.services.attachment_analysis.attachments import (
    classify_attachment_extension,
    has_double_extension,
    has_suspicious_filename_chars,
    is_executable_extension,
    is_office_document_extension,
    is_pdf_extension,
)


ATTACHMENT_HAS_EXECUTABLE_EXTENSION = "ATTACHMENT_HAS_EXECUTABLE_EXTENSION"
ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION = "ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION"
ATTACHMENT_HAS_DOUBLE_EXTENSION = "ATTACHMENT_HAS_DOUBLE_EXTENSION"
ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS = (
    "ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS"
)


@dataclass(frozen=True)
class AnalyzeAttachmentIndicatorsCommand:
    filename: str


@dataclass(frozen=True)
class AttachmentIndicatorsAnalysis:
    filename: str
    extension_category: str
    has_executable_extension: bool
    has_office_document_extension: bool
    has_pdf_extension: bool
    has_double_extension: bool
    has_suspicious_filename_chars: bool
    findings: list[str]


class AnalyzeAttachmentIndicatorsUseCase:
    def execute(
        self,
        command: AnalyzeAttachmentIndicatorsCommand,
    ) -> AttachmentIndicatorsAnalysis:
        filename = command.filename
        attachment_has_executable_extension = is_executable_extension(filename)
        attachment_has_office_document_extension = is_office_document_extension(
            filename
        )
        attachment_has_pdf_extension = is_pdf_extension(filename)
        attachment_has_double_extension = has_double_extension(filename)
        attachment_has_suspicious_filename_chars = has_suspicious_filename_chars(
            filename
        )
        finding_conditions = [
            (
                attachment_has_executable_extension,
                ATTACHMENT_HAS_EXECUTABLE_EXTENSION,
            ),
            (
                attachment_has_office_document_extension,
                ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION,
            ),
            (attachment_has_double_extension, ATTACHMENT_HAS_DOUBLE_EXTENSION),
            (
                attachment_has_suspicious_filename_chars,
                ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS,
            ),
        ]
        findings = [
            finding
            for condition, finding in finding_conditions
            if condition
        ]

        return AttachmentIndicatorsAnalysis(
            filename=filename,
            extension_category=classify_attachment_extension(filename),
            has_executable_extension=attachment_has_executable_extension,
            has_office_document_extension=attachment_has_office_document_extension,
            has_pdf_extension=attachment_has_pdf_extension,
            has_double_extension=attachment_has_double_extension,
            has_suspicious_filename_chars=attachment_has_suspicious_filename_chars,
            findings=findings,
        )
