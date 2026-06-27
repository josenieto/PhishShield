from dataclasses import dataclass

from domain.services.risk_scoring.risk_scores import (
    calculate_indicator_score,
    cap_risk_score,
    classify_risk_level,
    has_critical_indicators,
)


@dataclass(frozen=True)
class CalculateRiskScoreCommand:
    indicators: list[str]
    weights: dict[str, int]
    critical_indicators: set[str]
    min_score: int = 0
    max_score: int = 100


@dataclass(frozen=True)
class RiskScoreAnalysis:
    indicators: list[str]
    raw_score: int
    capped_score: int
    risk_level: str
    has_critical_indicators: bool


class CalculateRiskScoreUseCase:
    def execute(
        self,
        command: CalculateRiskScoreCommand,
    ) -> RiskScoreAnalysis:
        raw_score = calculate_indicator_score(
            command.indicators,
            command.weights,
        )
        capped_score = cap_risk_score(
            raw_score,
            min_score=command.min_score,
            max_score=command.max_score,
        )

        return RiskScoreAnalysis(
            indicators=command.indicators,
            raw_score=raw_score,
            capped_score=capped_score,
            risk_level=classify_risk_level(capped_score),
            has_critical_indicators=has_critical_indicators(
                command.indicators,
                command.critical_indicators,
            ),
        )
