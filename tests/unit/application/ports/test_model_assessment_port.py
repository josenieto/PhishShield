from application.models.model_assessment import (
    MODEL_ASSESSMENT_LABEL_SUSPICIOUS,
    MODEL_ASSESSMENT_STATUS_COMPLETED,
    ModelAssessment,
)
from application.ports.outbound.model_assessment import (
    AssessRawEmailWithModelCommand,
    ModelAssessmentPort,
)


class FakeModelAssessmentAdapter:
    def __init__(self) -> None:
        self.received_command: AssessRawEmailWithModelCommand | None = None

    def assess_raw_email(
        self,
        command: AssessRawEmailWithModelCommand,
    ) -> ModelAssessment:
        self.received_command = command
        return ModelAssessment(
            status=MODEL_ASSESSMENT_STATUS_COMPLETED,
            label=MODEL_ASSESSMENT_LABEL_SUSPICIOUS,
            confidence=0.77,
            summary="The message resembles a suspicious account verification lure.",
            signals=("Credential request wording",),
            model_name="local-model",
            model_version="0.1",
        )


def test_should_store_raw_email_model_assessment_command() -> None:
    command = AssessRawEmailWithModelCommand(
        raw_email=b"raw email bytes",
        filename="sample.eml",
        content_type="message/rfc822",
        max_input_bytes=200_000,
    )

    assert command.raw_email == b"raw email bytes"
    assert command.filename == "sample.eml"
    assert command.content_type == "message/rfc822"
    assert command.max_input_bytes == 200_000


def test_should_use_model_assessment_port_contract() -> None:
    adapter = FakeModelAssessmentAdapter()
    port: ModelAssessmentPort = adapter
    command = AssessRawEmailWithModelCommand(
        raw_email=b"raw email bytes",
        filename="sample.eml",
        content_type="message/rfc822",
        max_input_bytes=200_000,
    )

    assessment = port.assess_raw_email(command)

    assert adapter.received_command == command
    assert assessment == ModelAssessment(
        status=MODEL_ASSESSMENT_STATUS_COMPLETED,
        label=MODEL_ASSESSMENT_LABEL_SUSPICIOUS,
        confidence=0.77,
        summary="The message resembles a suspicious account verification lure.",
        signals=("Credential request wording",),
        model_name="local-model",
        model_version="0.1",
    )
