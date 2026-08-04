from dataclasses import dataclass
from typing import Protocol

from application.models.scope_assessment import ScopeAssessment


@dataclass(frozen=True)
class AssessEmailScopeCommand:
    subject: str
    body_text: str
    urls: tuple[str, ...]
    attachment_filenames: tuple[str, ...]


class ScopeAssessmentPort(Protocol):
    def assess_scope(self, command: AssessEmailScopeCommand) -> ScopeAssessment:
        ...
