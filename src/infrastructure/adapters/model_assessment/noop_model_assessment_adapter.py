from application.models.model_assessment import (
    MODEL_ASSESSMENT_LABEL_UNKNOWN,
    MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED,
    ModelAssessment,
)
from application.ports.outbound.model_assessment import AssessRawEmailWithModelCommand


class NoopModelAssessmentAdapter:
    def assess_raw_email(
        self,
        command: AssessRawEmailWithModelCommand,
    ) -> ModelAssessment:
        return ModelAssessment(
            status=MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED,
            label=MODEL_ASSESSMENT_LABEL_UNKNOWN,
            confidence=None,
            summary="",
            signals=(),
            model_name="",
            model_version="",
            error_message="",
        )
