from application.models.model_assessment import (
    MODEL_ASSESSMENT_LABEL_UNKNOWN,
    MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED,
    ModelAssessment,
)
from application.ports.outbound.model_assessment import (
    AssessRawEmailWithModelCommand,
    ModelAssessmentPort,
)
from infrastructure.adapters.model_assessment.noop_model_assessment_adapter import (
    NoopModelAssessmentAdapter,
)


def test_should_return_not_configured_model_assessment() -> None:
    adapter = NoopModelAssessmentAdapter()

    assessment = adapter.assess_raw_email(
        AssessRawEmailWithModelCommand(
            raw_email=b"raw email bytes",
            filename="sample.eml",
            content_type="message/rfc822",
            max_input_bytes=100_000,
        )
    )

    assert assessment == ModelAssessment(
        status=MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED,
        label=MODEL_ASSESSMENT_LABEL_UNKNOWN,
        confidence=None,
        summary="",
        signals=(),
        model_name="",
        model_version="",
        error_message="",
    )


def test_should_implement_model_assessment_port_contract() -> None:
    adapter: ModelAssessmentPort = NoopModelAssessmentAdapter()

    assessment = adapter.assess_raw_email(
        AssessRawEmailWithModelCommand(
            raw_email=b"raw email bytes",
            filename="sample.eml",
            content_type="message/rfc822",
            max_input_bytes=100_000,
        )
    )

    assert assessment.status == MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED
    assert assessment.label == MODEL_ASSESSMENT_LABEL_UNKNOWN
    assert assessment.confidence is None
    assert assessment.signals == ()
