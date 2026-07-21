from dataclasses import dataclass

from application.models.model_assessment import ModelAssessment
from application.ports.outbound.model_assessment import (
    AssessRawEmailWithModelCommand,
    ModelAssessmentPort,
)


@dataclass(frozen=True)
class AssessRawEmailWithModelUseCaseCommand:
    raw_email: bytes
    filename: str
    content_type: str
    max_input_bytes: int


class AssessRawEmailWithModelUseCase:
    def __init__(self, model_assessment_port: ModelAssessmentPort) -> None:
        self._model_assessment_port = model_assessment_port

    def execute(
        self,
        command: AssessRawEmailWithModelUseCaseCommand,
    ) -> ModelAssessment:
        return self._model_assessment_port.assess_raw_email(
            AssessRawEmailWithModelCommand(
                raw_email=command.raw_email,
                filename=command.filename,
                content_type=command.content_type,
                max_input_bytes=command.max_input_bytes,
            )
        )
