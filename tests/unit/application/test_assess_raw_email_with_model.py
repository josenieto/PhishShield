from application.models.model_assessment import (
    MODEL_ASSESSMENT_LABEL_SUSPICIOUS,
    MODEL_ASSESSMENT_STATUS_COMPLETED,
    ModelAssessment,
)
from application.ports.outbound.model_assessment import (
    AssessRawEmailWithModelCommand,
    ModelAssessmentPort,
)
from application.use_cases.assess_raw_email_with_model import (
    AssessRawEmailWithModelUseCase,
    AssessRawEmailWithModelUseCaseCommand,
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
            confidence=0.73,
            summary="The message resembles a suspicious verification lure.",
            signals=("Credential request wording", "Unusual link pattern"),
            model_name="local-model",
            model_version="0.1",
        )


def test_should_delegate_raw_email_assessment_to_model_assessment_port() -> None:
    adapter = FakeModelAssessmentAdapter()
    use_case = AssessRawEmailWithModelUseCase(model_assessment_port=adapter)
    command = AssessRawEmailWithModelUseCaseCommand(
        raw_email=b"raw email bytes",
        filename="sample.eml",
        content_type="message/rfc822",
        max_input_bytes=250_000,
    )

    assessment = use_case.execute(command)

    assert adapter.received_command == AssessRawEmailWithModelCommand(
        raw_email=b"raw email bytes",
        filename="sample.eml",
        content_type="message/rfc822",
        max_input_bytes=250_000,
    )
    assert assessment == ModelAssessment(
        status=MODEL_ASSESSMENT_STATUS_COMPLETED,
        label=MODEL_ASSESSMENT_LABEL_SUSPICIOUS,
        confidence=0.73,
        summary="The message resembles a suspicious verification lure.",
        signals=("Credential request wording", "Unusual link pattern"),
        model_name="local-model",
        model_version="0.1",
    )


def test_should_accept_model_assessment_port_protocol_dependency() -> None:
    adapter = FakeModelAssessmentAdapter()
    port: ModelAssessmentPort = adapter
    use_case = AssessRawEmailWithModelUseCase(model_assessment_port=port)

    assessment = use_case.execute(
        AssessRawEmailWithModelUseCaseCommand(
            raw_email=b"another raw email",
            filename="another.eml",
            content_type="message/rfc822",
            max_input_bytes=100_000,
        )
    )

    assert assessment.status == MODEL_ASSESSMENT_STATUS_COMPLETED
    assert adapter.received_command is not None
    assert adapter.received_command.raw_email == b"another raw email"
    assert adapter.received_command.filename == "another.eml"
    assert adapter.received_command.content_type == "message/rfc822"
    assert adapter.received_command.max_input_bytes == 100_000
