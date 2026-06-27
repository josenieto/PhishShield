import pytest

from application.use_cases.calculate_risk_score import (
    CalculateRiskScoreCommand,
    CalculateRiskScoreUseCase,
)


def test_should_calculate_risk_score_from_weighted_indicators() -> None:
    use_case = CalculateRiskScoreUseCase()

    result = use_case.execute(
        CalculateRiskScoreCommand(
            indicators=[
                "DOMAIN_CONTAINS_PUNYCODE",
                "URL_HAS_EMBEDDED_CREDENTIALS",
            ],
            weights={
                "DOMAIN_CONTAINS_PUNYCODE": 30,
                "URL_HAS_EMBEDDED_CREDENTIALS": 25,
            },
            critical_indicators=set(),
        )
    )

    assert result.indicators == [
        "DOMAIN_CONTAINS_PUNYCODE",
        "URL_HAS_EMBEDDED_CREDENTIALS",
    ]
    assert result.raw_score == 55
    assert result.capped_score == 55
    assert result.risk_level == "HIGH"
    assert result.has_critical_indicators is False


def test_should_ignore_unknown_indicators() -> None:
    use_case = CalculateRiskScoreUseCase()

    result = use_case.execute(
        CalculateRiskScoreCommand(
            indicators=[
                "DOMAIN_CONTAINS_PUNYCODE",
                "UNKNOWN_INDICATOR",
            ],
            weights={"DOMAIN_CONTAINS_PUNYCODE": 30},
            critical_indicators=set(),
        )
    )

    assert result.raw_score == 30
    assert result.capped_score == 30
    assert result.risk_level == "MEDIUM"


def test_should_cap_risk_score_at_maximum() -> None:
    use_case = CalculateRiskScoreUseCase()

    result = use_case.execute(
        CalculateRiskScoreCommand(
            indicators=[
                "DOMAIN_CONTAINS_PUNYCODE",
                "URL_HAS_EMBEDDED_CREDENTIALS",
                "AUTHENTICATION_DMARC_FAILED",
            ],
            weights={
                "DOMAIN_CONTAINS_PUNYCODE": 40,
                "URL_HAS_EMBEDDED_CREDENTIALS": 35,
                "AUTHENTICATION_DMARC_FAILED": 50,
            },
            critical_indicators=set(),
            max_score=100,
        )
    )

    assert result.raw_score == 125
    assert result.capped_score == 100
    assert result.risk_level == "CRITICAL"


def test_should_cap_negative_risk_score_at_minimum() -> None:
    use_case = CalculateRiskScoreUseCase()

    result = use_case.execute(
        CalculateRiskScoreCommand(
            indicators=["TRUSTED_INTERNAL_SENDER"],
            weights={"TRUSTED_INTERNAL_SENDER": -10},
            critical_indicators=set(),
        )
    )

    assert result.raw_score == -10
    assert result.capped_score == 0
    assert result.risk_level == "LOW"


def test_should_detect_critical_indicator() -> None:
    use_case = CalculateRiskScoreUseCase()

    result = use_case.execute(
        CalculateRiskScoreCommand(
            indicators=["AUTHENTICATION_DMARC_FAILED"],
            weights={"AUTHENTICATION_DMARC_FAILED": 30},
            critical_indicators={"AUTHENTICATION_DMARC_FAILED"},
        )
    )

    assert result.raw_score == 30
    assert result.risk_level == "MEDIUM"
    assert result.has_critical_indicators is True


def test_should_raise_error_when_risk_score_limits_are_invalid() -> None:
    use_case = CalculateRiskScoreUseCase()

    with pytest.raises(ValueError):
        use_case.execute(
            CalculateRiskScoreCommand(
                indicators=["DOMAIN_CONTAINS_PUNYCODE"],
                weights={"DOMAIN_CONTAINS_PUNYCODE": 30},
                critical_indicators=set(),
                min_score=100,
                max_score=0,
            )
        )
