from dataclasses import dataclass
from typing import Protocol

from application.models.model_assessment import ModelAssessment


@dataclass(frozen=True)
class AssessRawEmailWithModelCommand:
    raw_email: bytes
    filename: str
    content_type: str
    max_input_bytes: int


class ModelAssessmentPort(Protocol):
    def assess_raw_email(
        self,
        command: AssessRawEmailWithModelCommand,
    ) -> ModelAssessment:
        """Return an advisory model assessment for the original raw email."""
