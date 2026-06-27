AUTHENTICATION_LOW = "LOW"
AUTHENTICATION_MEDIUM = "MEDIUM"
AUTHENTICATION_HIGH = "HIGH"
AUTHENTICATION_CRITICAL = "CRITICAL"
AUTHENTICATION_UNKNOWN = "UNKNOWN"

FINDING_AUTHENTICATION_SPF_FAILED = "AUTHENTICATION_SPF_FAILED"
FINDING_AUTHENTICATION_DKIM_FAILED = "AUTHENTICATION_DKIM_FAILED"
FINDING_AUTHENTICATION_DMARC_FAILED = "AUTHENTICATION_DMARC_FAILED"
FINDING_AUTHENTICATION_HAS_MULTIPLE_FAILURES = "AUTHENTICATION_HAS_MULTIPLE_FAILURES"
FINDING_AUTHENTICATION_RESULTS_UNKNOWN = "AUTHENTICATION_RESULTS_UNKNOWN"

_AUTHENTICATION_PASS = "pass"
_AUTHENTICATION_FAIL = "fail"
_AUTHENTICATION_SOFTFAIL = "softfail"
_AUTHENTICATION_NEUTRAL = "neutral"
_AUTHENTICATION_NONE = "none"
_AUTHENTICATION_TEMPERROR = "temperror"
_AUTHENTICATION_PERMERROR = "permerror"
_AUTHENTICATION_UNKNOWN = "unknown"

_KNOWN_RESULTS: frozenset[str] = frozenset(
    {
        _AUTHENTICATION_PASS,
        _AUTHENTICATION_FAIL,
        _AUTHENTICATION_SOFTFAIL,
        _AUTHENTICATION_NEUTRAL,
        _AUTHENTICATION_NONE,
        _AUTHENTICATION_TEMPERROR,
        _AUTHENTICATION_PERMERROR,
        _AUTHENTICATION_UNKNOWN,
    }
)

_FAILURE_RESULTS: frozenset[str] = frozenset(
    {
        _AUTHENTICATION_FAIL,
        _AUTHENTICATION_SOFTFAIL,
        _AUTHENTICATION_PERMERROR,
    }
)

_WEAK_RESULTS: frozenset[str] = frozenset(
    {
        _AUTHENTICATION_NEUTRAL,
        _AUTHENTICATION_NONE,
        _AUTHENTICATION_TEMPERROR,
        _AUTHENTICATION_UNKNOWN,
    }
)

_FAILURE_OR_WEAK_RESULTS = _FAILURE_RESULTS | _WEAK_RESULTS


def is_authentication_aligned(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> bool:
    """Return True when DMARC passes and either SPF or DKIM passes."""
    normalized_spf = _normalize_authentication_result(spf_result)
    normalized_dkim = _normalize_authentication_result(dkim_result)
    normalized_dmarc = _normalize_authentication_result(dmarc_result)

    return (
        normalized_dmarc == _AUTHENTICATION_PASS
        and (
            normalized_spf == _AUTHENTICATION_PASS
            or normalized_dkim == _AUTHENTICATION_PASS
        )
    )


def has_authentication_failure(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> bool:
    """Return True when SPF, DKIM, or DMARC has a relevant failure result."""
    return any(
        result in _FAILURE_RESULTS
        for result in _normalize_authentication_results(
            spf_result,
            dkim_result,
            dmarc_result,
        )
    )


def classify_authentication_risk(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> str:
    """Classify authentication risk from already computed SPF, DKIM, and DMARC results."""
    normalized_spf, normalized_dkim, normalized_dmarc = _normalize_authentication_results(
        spf_result,
        dkim_result,
        dmarc_result,
    )

    if _are_all_unknown(normalized_spf, normalized_dkim, normalized_dmarc):
        return AUTHENTICATION_UNKNOWN

    if normalized_dmarc in _FAILURE_RESULTS:
        if (
            normalized_spf in _FAILURE_OR_WEAK_RESULTS
            or normalized_dkim in _FAILURE_OR_WEAK_RESULTS
        ):
            return AUTHENTICATION_CRITICAL

        return AUTHENTICATION_HIGH

    if normalized_spf in _FAILURE_RESULTS or normalized_dkim in _FAILURE_RESULTS:
        return AUTHENTICATION_MEDIUM

    if is_authentication_aligned(spf_result, dkim_result, dmarc_result):
        return AUTHENTICATION_LOW

    return AUTHENTICATION_MEDIUM


def summarize_authentication_findings(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> list[str]:
    """Return finding codes for relevant authentication failures."""
    normalized_spf, normalized_dkim, normalized_dmarc = _normalize_authentication_results(
        spf_result,
        dkim_result,
        dmarc_result,
    )

    if _are_all_unknown(normalized_spf, normalized_dkim, normalized_dmarc):
        return [FINDING_AUTHENTICATION_RESULTS_UNKNOWN]

    findings = []

    if normalized_spf in _FAILURE_RESULTS:
        findings.append(FINDING_AUTHENTICATION_SPF_FAILED)

    if normalized_dkim in _FAILURE_RESULTS:
        findings.append(FINDING_AUTHENTICATION_DKIM_FAILED)

    if normalized_dmarc in _FAILURE_RESULTS:
        findings.append(FINDING_AUTHENTICATION_DMARC_FAILED)

    if len(findings) > 1:
        findings.append(FINDING_AUTHENTICATION_HAS_MULTIPLE_FAILURES)

    return findings


def _normalize_authentication_results(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> tuple[str, str, str]:
    return (
        _normalize_authentication_result(spf_result),
        _normalize_authentication_result(dkim_result),
        _normalize_authentication_result(dmarc_result),
    )


def _normalize_authentication_result(result: str) -> str:
    normalized_result = result.strip().lower()

    if normalized_result in _KNOWN_RESULTS:
        return normalized_result

    return _AUTHENTICATION_UNKNOWN


def _are_all_unknown(*results: str) -> bool:
    return all(result == _AUTHENTICATION_UNKNOWN for result in results)
