from application.use_cases.analyze_domain_indicators import (
    AnalyzeDomainIndicatorsCommand,
    AnalyzeDomainIndicatorsUseCase,
)


def test_should_analyze_normal_domain_without_findings() -> None:
    use_case = AnalyzeDomainIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeDomainIndicatorsCommand(
            domain="example.com",
            suspicious_tlds={"zip"},
        )
    )

    assert result.domain == "example.com"
    assert result.labels == ["example", "com"]
    assert result.scripts == {"LATIN"}
    assert result.contains_punycode is False
    assert result.has_mixed_scripts is False
    assert result.has_confusable_characters is False
    assert result.confusable_characters == []
    assert result.has_suspicious_subdomain_depth is False
    assert result.looks_like_ip_address is False
    assert result.has_suspicious_tld is False
    assert result.findings == []


def test_should_report_punycode_domain_finding() -> None:
    use_case = AnalyzeDomainIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeDomainIndicatorsCommand(
            domain="xn--paypl-3ve.com",
            suspicious_tlds={"zip"},
        )
    )

    assert result.contains_punycode is True
    assert result.findings == ["DOMAIN_CONTAINS_PUNYCODE"]


def test_should_report_homoglyph_domain_findings() -> None:
    use_case = AnalyzeDomainIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeDomainIndicatorsCommand(
            domain="microsоft.com",
            suspicious_tlds={"zip"},
        )
    )

    assert result.has_mixed_scripts is True
    assert result.has_confusable_characters is True
    assert result.confusable_characters == ["о"]
    assert result.findings == [
        "DOMAIN_HAS_MIXED_SCRIPTS",
        "DOMAIN_HAS_CONFUSABLE_CHARACTERS",
    ]


def test_should_report_suspicious_subdomain_depth_finding() -> None:
    use_case = AnalyzeDomainIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeDomainIndicatorsCommand(
            domain="a.b.c.d.com",
            suspicious_tlds={"zip"},
        )
    )

    assert result.has_suspicious_subdomain_depth is True
    assert result.findings == ["DOMAIN_HAS_SUSPICIOUS_DEPTH"]


def test_should_report_ip_address_host_finding() -> None:
    use_case = AnalyzeDomainIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeDomainIndicatorsCommand(
            domain="192.168.1.1",
            suspicious_tlds={"zip"},
        )
    )

    assert result.looks_like_ip_address is True
    assert result.findings == ["DOMAIN_LOOKS_LIKE_IP_ADDRESS"]


def test_should_report_suspicious_tld_finding() -> None:
    use_case = AnalyzeDomainIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeDomainIndicatorsCommand(
            domain="example.zip",
            suspicious_tlds={"zip"},
        )
    )

    assert result.has_suspicious_tld is True
    assert result.findings == ["DOMAIN_HAS_SUSPICIOUS_TLD"]


def test_should_report_multiple_domain_findings_in_order() -> None:
    use_case = AnalyzeDomainIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeDomainIndicatorsCommand(
            domain="a.b.c.d.xn--paypl-3ve.zip",
            suspicious_tlds={"zip"},
        )
    )

    assert result.contains_punycode is True
    assert result.has_suspicious_subdomain_depth is True
    assert result.has_suspicious_tld is True
    assert result.findings == [
        "DOMAIN_CONTAINS_PUNYCODE",
        "DOMAIN_HAS_SUSPICIOUS_DEPTH",
        "DOMAIN_HAS_SUSPICIOUS_TLD",
    ]
