from application.use_cases.analyze_attachment_indicators import (
    AnalyzeAttachmentIndicatorsCommand,
    AnalyzeAttachmentIndicatorsUseCase,
)


def test_should_analyze_pdf_attachment_without_findings() -> None:
    use_case = AnalyzeAttachmentIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeAttachmentIndicatorsCommand(filename="invoice.pdf")
    )

    assert result.filename == "invoice.pdf"
    assert result.extension_category == "PDF"
    assert result.has_executable_extension is False
    assert result.has_office_document_extension is False
    assert result.has_pdf_extension is True
    assert result.has_double_extension is False
    assert result.has_suspicious_filename_chars is False
    assert result.findings == []


def test_should_report_executable_attachment_finding() -> None:
    use_case = AnalyzeAttachmentIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeAttachmentIndicatorsCommand(filename="payload.exe")
    )

    assert result.extension_category == "EXECUTABLE"
    assert result.has_executable_extension is True
    assert result.findings == ["ATTACHMENT_HAS_EXECUTABLE_EXTENSION"]


def test_should_report_office_document_attachment_finding() -> None:
    use_case = AnalyzeAttachmentIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeAttachmentIndicatorsCommand(filename="document.docm")
    )

    assert result.extension_category == "OFFICE"
    assert result.has_office_document_extension is True
    assert result.findings == ["ATTACHMENT_HAS_OFFICE_DOCUMENT_EXTENSION"]


def test_should_report_double_extension_finding() -> None:
    use_case = AnalyzeAttachmentIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeAttachmentIndicatorsCommand(filename="invoice.pdf.exe")
    )

    assert result.extension_category == "EXECUTABLE"
    assert result.has_executable_extension is True
    assert result.has_double_extension is True
    assert result.findings == [
        "ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
        "ATTACHMENT_HAS_DOUBLE_EXTENSION",
    ]


def test_should_report_suspicious_filename_character_finding() -> None:
    use_case = AnalyzeAttachmentIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeAttachmentIndicatorsCommand(filename="invоice.pdf")
    )

    assert result.extension_category == "PDF"
    assert result.has_suspicious_filename_chars is True
    assert result.findings == ["ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS"]


def test_should_report_multiple_attachment_findings_in_order() -> None:
    use_case = AnalyzeAttachmentIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeAttachmentIndicatorsCommand(filename="invоice.docm.exe")
    )

    assert result.extension_category == "EXECUTABLE"
    assert result.has_executable_extension is True
    assert result.has_office_document_extension is False
    assert result.has_pdf_extension is False
    assert result.has_double_extension is True
    assert result.has_suspicious_filename_chars is True
    assert result.findings == [
        "ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
        "ATTACHMENT_HAS_DOUBLE_EXTENSION",
        "ATTACHMENT_HAS_SUSPICIOUS_FILENAME_CHARS",
    ]
