from dataclasses import dataclass


MODEL_ASSESSMENT_STATUS_COMPLETED = "completed"
MODEL_ASSESSMENT_STATUS_NOT_CONFIGURED = "not_configured"
MODEL_ASSESSMENT_STATUS_FAILED = "failed"
MODEL_ASSESSMENT_STATUS_SKIPPED = "skipped"
MODEL_ASSESSMENT_STATUS_INCONCLUSIVE = "inconclusive"

MODEL_ASSESSMENT_LABEL_BENIGN = "benign"
MODEL_ASSESSMENT_LABEL_SUSPICIOUS = "suspicious"
MODEL_ASSESSMENT_LABEL_PHISHING = "phishing"
MODEL_ASSESSMENT_LABEL_UNKNOWN = "unknown"
MODEL_ASSESSMENT_LABEL_INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class ModelAssessment:
    status: str
    label: str
    confidence: float | None
    summary: str
    signals: tuple[str, ...]
    model_name: str
    model_version: str
    error_message: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "signals", tuple(self.signals))

        if self.confidence is None:
            return

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
