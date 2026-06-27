import pytest

from domain.services.authentication_analysis.authentication_results import (
    AUTHENTICATION_CRITICAL,
    AUTHENTICATION_HIGH,
    AUTHENTICATION_LOW,
    AUTHENTICATION_MEDIUM,
    AUTHENTICATION_UNKNOWN,
    FINDING_AUTHENTICATION_DKIM_FAILED,
    FINDING_AUTHENTICATION_DMARC_FAILED,
    FINDING_AUTHENTICATION_HAS_MULTIPLE_FAILURES,
    FINDING_AUTHENTICATION_RESULTS_UNKNOWN,
    FINDING_AUTHENTICATION_SPF_FAILED,
    classify_authentication_risk,
    has_authentication_failure,
    is_authentication_aligned,
    summarize_authentication_findings,
)


@pytest.mark.parametrize(
    ("spf_result", "dkim_result", "dmarc_result"),
    [
        ("pass", "pass", "pass"),
        ("fail", "pass", "pass"),
        ("PASS", "none", "PASS"),
        ("none", " pass ", "pass"),
        ("unknown-value", "pass", "pass"),
    ],
)
def test_should_detect_aligned_authentication_when_dmarc_passes_and_sender_auth_passes(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> None:
    assert is_authentication_aligned(spf_result, dkim_result, dmarc_result) is True


@pytest.mark.parametrize(
    ("spf_result", "dkim_result", "dmarc_result"),
    [
        ("pass", "pass", "fail"),
        ("neutral", "none", "pass"),
        ("", "", ""),
    ],
)
def test_should_return_false_when_authentication_is_not_aligned(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> None:
    assert is_authentication_aligned(spf_result, dkim_result, dmarc_result) is False


@pytest.mark.parametrize(
    ("spf_result", "dkim_result", "dmarc_result"),
    [
        ("fail", "pass", "pass"),
        ("pass", "softfail", "pass"),
        ("pass", "pass", "permerror"),
        ("FAIL", "SOFTFAIL", "PERMERROR"),
    ],
)
def test_should_detect_relevant_authentication_failure(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> None:
    assert has_authentication_failure(spf_result, dkim_result, dmarc_result) is True


@pytest.mark.parametrize(
    ("spf_result", "dkim_result", "dmarc_result"),
    [
        ("pass", "pass", "pass"),
        ("neutral", "none", "pass"),
        ("temperror", "unknown", "none"),
        ("", "", ""),
    ],
)
def test_should_return_false_when_authentication_has_no_relevant_failure(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> None:
    assert has_authentication_failure(spf_result, dkim_result, dmarc_result) is False


@pytest.mark.parametrize(
    ("spf_result", "dkim_result", "dmarc_result", "expected_risk"),
    [
        ("", "", "", AUTHENTICATION_UNKNOWN),
        ("unknown", "unknown", "unknown", AUTHENTICATION_UNKNOWN),
        ("pass", "none", "pass", AUTHENTICATION_LOW),
        ("none", "pass", "pass", AUTHENTICATION_LOW),
        ("fail", "pass", "pass", AUTHENTICATION_MEDIUM),
        ("neutral", "none", "pass", AUTHENTICATION_MEDIUM),
        ("pass", "pass", "fail", AUTHENTICATION_HIGH),
        ("fail", "none", "fail", AUTHENTICATION_CRITICAL),
        ("none", "softfail", "fail", AUTHENTICATION_CRITICAL),
        ("permerror", "temperror", "fail", AUTHENTICATION_CRITICAL),
    ],
)
def test_should_classify_authentication_risk(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
    expected_risk: str,
) -> None:
    assert classify_authentication_risk(spf_result, dkim_result, dmarc_result) == expected_risk


@pytest.mark.parametrize(
    ("spf_result", "dkim_result", "dmarc_result", "expected_findings"),
    [
        ("pass", "pass", "pass", []),
        ("fail", "pass", "pass", [FINDING_AUTHENTICATION_SPF_FAILED]),
        ("pass", "softfail", "pass", [FINDING_AUTHENTICATION_DKIM_FAILED]),
        ("pass", "pass", "permerror", [FINDING_AUTHENTICATION_DMARC_FAILED]),
        (
            "fail",
            "softfail",
            "fail",
            [
                FINDING_AUTHENTICATION_SPF_FAILED,
                FINDING_AUTHENTICATION_DKIM_FAILED,
                FINDING_AUTHENTICATION_DMARC_FAILED,
                FINDING_AUTHENTICATION_HAS_MULTIPLE_FAILURES,
            ],
        ),
        ("", "", "", [FINDING_AUTHENTICATION_RESULTS_UNKNOWN]),
    ],
)
def test_should_summarize_authentication_findings(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
    expected_findings: list[str],
) -> None:
    assert summarize_authentication_findings(
        spf_result,
        dkim_result,
        dmarc_result,
    ) == expected_findings
