import pytest

from domain.services.risk_scoring.risk_scores import (
    calculate_indicator_score,
    cap_risk_score,
    classify_risk_level,
    combine_risk_scores,
    has_critical_indicators,
    RISK_CRITICAL,
    RISK_HIGH,
    RISK_LOW,
    RISK_MEDIUM,
)


def test_should_calculate_score_for_known_indicators() -> None:
    indicators = [
        "DOMAIN_CONTAINS_PUNYCODE",
        "URL_HAS_EMBEDDED_CREDENTIALS",
    ]
    weights = {
        "DOMAIN_CONTAINS_PUNYCODE": 30,
        "URL_HAS_EMBEDDED_CREDENTIALS": 25,
    }

    assert calculate_indicator_score(indicators, weights) == 55


def test_should_ignore_unknown_indicators() -> None:
    indicators = [
        "DOMAIN_CONTAINS_PUNYCODE",
        "UNKNOWN_INDICATOR",
    ]
    weights = {"DOMAIN_CONTAINS_PUNYCODE": 30}

    assert calculate_indicator_score(indicators, weights) == 30


def test_should_return_zero_when_indicators_are_empty() -> None:
    assert calculate_indicator_score([], {"DOMAIN_CONTAINS_PUNYCODE": 30}) == 0


def test_should_return_zero_when_weights_are_empty() -> None:
    assert calculate_indicator_score(["DOMAIN_CONTAINS_PUNYCODE"], {}) == 0


def test_should_count_duplicate_indicators() -> None:
    indicators = [
        "URL_HAS_EMBEDDED_CREDENTIALS",
        "URL_HAS_EMBEDDED_CREDENTIALS",
    ]
    weights = {"URL_HAS_EMBEDDED_CREDENTIALS": 25}

    assert calculate_indicator_score(indicators, weights) == 50


def test_should_allow_negative_weights() -> None:
    indicators = [
        "DOMAIN_CONTAINS_PUNYCODE",
        "TRUSTED_INTERNAL_SENDER",
    ]
    weights = {
        "DOMAIN_CONTAINS_PUNYCODE": 30,
        "TRUSTED_INTERNAL_SENDER": -10,
    }

    assert calculate_indicator_score(indicators, weights) == 20


def test_should_combine_risk_scores() -> None:
    assert combine_risk_scores([10, 20, 30]) == 60


def test_should_return_zero_when_risk_scores_are_empty() -> None:
    assert combine_risk_scores([]) == 0


def test_should_allow_negative_partial_risk_scores() -> None:
    assert combine_risk_scores([10, -5, 20]) == 25


def test_should_cap_score_below_default_minimum() -> None:
    assert cap_risk_score(-10) == 0


def test_should_cap_score_above_default_maximum() -> None:
    assert cap_risk_score(120) == 100


def test_should_keep_score_inside_default_range() -> None:
    assert cap_risk_score(50) == 50


def test_should_cap_score_with_custom_limits() -> None:
    assert cap_risk_score(150, min_score=10, max_score=80) == 80


def test_should_raise_error_when_risk_score_limits_are_invalid() -> None:
    with pytest.raises(ValueError):
        cap_risk_score(50, min_score=100, max_score=0)


@pytest.mark.parametrize(
    ("score", "expected_risk_level"),
    [
        (-10, RISK_LOW),
        (0, RISK_LOW),
        (24, RISK_LOW),
        (25, RISK_MEDIUM),
        (49, RISK_MEDIUM),
        (50, RISK_HIGH),
        (74, RISK_HIGH),
        (75, RISK_CRITICAL),
        (100, RISK_CRITICAL),
    ],
)
def test_should_classify_risk_level(
    score: int,
    expected_risk_level: str,
) -> None:
    assert classify_risk_level(score) == expected_risk_level


def test_should_detect_critical_indicator() -> None:
    indicators = [
        "DOMAIN_CONTAINS_PUNYCODE",
        "AUTHENTICATION_DMARC_FAILED",
    ]
    critical_indicators = {"AUTHENTICATION_DMARC_FAILED"}

    assert has_critical_indicators(indicators, critical_indicators) is True


def test_should_return_false_when_no_critical_indicator_is_present() -> None:
    indicators = [
        "DOMAIN_CONTAINS_PUNYCODE",
        "URL_HAS_EMBEDDED_CREDENTIALS",
    ]
    critical_indicators = {"AUTHENTICATION_DMARC_FAILED"}

    assert has_critical_indicators(indicators, critical_indicators) is False


def test_should_return_false_when_indicator_list_is_empty() -> None:
    assert has_critical_indicators([], {"AUTHENTICATION_DMARC_FAILED"}) is False


def test_should_return_false_when_critical_indicator_set_is_empty() -> None:
    assert has_critical_indicators(["AUTHENTICATION_DMARC_FAILED"], set()) is False


def test_should_detect_duplicate_critical_indicator() -> None:
    indicators = [
        "AUTHENTICATION_DMARC_FAILED",
        "AUTHENTICATION_DMARC_FAILED",
    ]
    critical_indicators = {"AUTHENTICATION_DMARC_FAILED"}

    assert has_critical_indicators(indicators, critical_indicators) is True
