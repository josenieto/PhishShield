from application.use_cases.analyze_url_indicators import (
    AnalyzeUrlIndicatorsCommand,
    AnalyzeUrlIndicatorsUseCase,
)


def test_should_analyze_normal_url_without_findings() -> None:
    use_case = AnalyzeUrlIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeUrlIndicatorsCommand(
            url="https://example.com/login",
            allowed_schemes={"https"},
            known_shorteners={"bit.ly"},
        )
    )

    assert result.url == "https://example.com/login"
    assert result.scheme == "https"
    assert result.domain == "example.com"
    assert result.query_parameter_count == 0
    assert result.is_scheme_allowed is True
    assert result.has_suspicious_scheme is False
    assert result.has_embedded_credentials is False
    assert result.has_suspicious_query_density is False
    assert result.uses_known_shortener_domain is False
    assert result.findings == []


def test_should_report_disallowed_url_scheme_finding() -> None:
    use_case = AnalyzeUrlIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeUrlIndicatorsCommand(
            url="ftp://example.com/file",
            allowed_schemes={"http", "https"},
            known_shorteners={"bit.ly"},
        )
    )

    assert result.scheme == "ftp"
    assert result.is_scheme_allowed is False
    assert result.findings == ["URL_SCHEME_NOT_ALLOWED"]


def test_should_report_suspicious_url_scheme_finding() -> None:
    use_case = AnalyzeUrlIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeUrlIndicatorsCommand(
            url="javascript:alert(1)",
            allowed_schemes={"http", "https"},
            known_shorteners={"bit.ly"},
        )
    )

    assert result.scheme == "javascript"
    assert result.is_scheme_allowed is False
    assert result.has_suspicious_scheme is True
    assert result.findings == [
        "URL_SCHEME_NOT_ALLOWED",
        "URL_HAS_SUSPICIOUS_SCHEME",
    ]


def test_should_report_embedded_credentials_finding() -> None:
    use_case = AnalyzeUrlIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeUrlIndicatorsCommand(
            url="https://user:pass@example.com/login",
            allowed_schemes={"https"},
            known_shorteners={"bit.ly"},
        )
    )

    assert result.domain == "example.com"
    assert result.has_embedded_credentials is True
    assert result.findings == ["URL_HAS_EMBEDDED_CREDENTIALS"]


def test_should_report_suspicious_query_density_finding() -> None:
    use_case = AnalyzeUrlIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeUrlIndicatorsCommand(
            url="https://example.com?a=1&b=2&c=3&d=4",
            allowed_schemes={"https"},
            known_shorteners={"bit.ly"},
            query_density_threshold=3,
        )
    )

    assert result.query_parameter_count == 4
    assert result.has_suspicious_query_density is True
    assert result.findings == ["URL_HAS_SUSPICIOUS_QUERY_DENSITY"]


def test_should_report_known_shortener_domain_finding() -> None:
    use_case = AnalyzeUrlIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeUrlIndicatorsCommand(
            url="https://bit.ly/abc",
            allowed_schemes={"https"},
            known_shorteners={"bit.ly"},
        )
    )

    assert result.domain == "bit.ly"
    assert result.uses_known_shortener_domain is True
    assert result.findings == ["URL_USES_KNOWN_SHORTENER_DOMAIN"]


def test_should_report_multiple_url_findings_in_order() -> None:
    use_case = AnalyzeUrlIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeUrlIndicatorsCommand(
            url="javascript://user:pass@bit.ly/path?a=1&b=2",
            allowed_schemes={"https"},
            known_shorteners={"bit.ly"},
            query_density_threshold=1,
        )
    )

    assert result.scheme == "javascript"
    assert result.domain == "bit.ly"
    assert result.query_parameter_count == 2
    assert result.is_scheme_allowed is False
    assert result.has_suspicious_scheme is True
    assert result.has_embedded_credentials is False
    assert result.has_suspicious_query_density is True
    assert result.uses_known_shortener_domain is True
    assert result.findings == [
        "URL_SCHEME_NOT_ALLOWED",
        "URL_HAS_SUSPICIOUS_SCHEME",
        "URL_HAS_SUSPICIOUS_QUERY_DENSITY",
        "URL_USES_KNOWN_SHORTENER_DOMAIN",
    ]


def test_should_return_safe_result_for_malformed_url() -> None:
    use_case = AnalyzeUrlIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeUrlIndicatorsCommand(
            url="https://[invalid",
            allowed_schemes={"https"},
            known_shorteners={"bit.ly"},
        )
    )

    assert result.url == "https://[invalid"
    assert result.scheme == ""
    assert result.domain == ""
    assert result.query_parameter_count == 0
    assert result.is_scheme_allowed is False
    assert result.findings == ["URL_SCHEME_NOT_ALLOWED"]
