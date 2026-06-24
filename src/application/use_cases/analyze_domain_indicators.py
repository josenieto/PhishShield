from dataclasses import dataclass

from domain.services.domain_analysis.domains import (
    contains_punycode,
    has_suspicious_subdomain_depth,
    has_suspicious_tld,
    looks_like_ip_address_host,
    split_domain_labels,
)
from domain.services.homoglyphs.confusables import (
    contains_confusable_characters,
    find_confusable_characters,
)
from domain.services.homoglyphs.scripts import (
    contains_mixed_scripts,
    detect_unicode_scripts,
)


DOMAIN_CONTAINS_PUNYCODE = "DOMAIN_CONTAINS_PUNYCODE"
DOMAIN_HAS_MIXED_SCRIPTS = "DOMAIN_HAS_MIXED_SCRIPTS"
DOMAIN_HAS_CONFUSABLE_CHARACTERS = "DOMAIN_HAS_CONFUSABLE_CHARACTERS"
DOMAIN_HAS_SUSPICIOUS_DEPTH = "DOMAIN_HAS_SUSPICIOUS_DEPTH"
DOMAIN_LOOKS_LIKE_IP_ADDRESS = "DOMAIN_LOOKS_LIKE_IP_ADDRESS"
DOMAIN_HAS_SUSPICIOUS_TLD = "DOMAIN_HAS_SUSPICIOUS_TLD"


@dataclass(frozen=True)
class AnalyzeDomainIndicatorsCommand:
    domain: str
    suspicious_tlds: set[str]
    max_subdomain_depth: int = 4


@dataclass(frozen=True)
class DomainIndicatorsAnalysis:
    domain: str
    labels: list[str]
    scripts: set[str]
    contains_punycode: bool
    has_mixed_scripts: bool
    has_confusable_characters: bool
    confusable_characters: list[str]
    has_suspicious_subdomain_depth: bool
    looks_like_ip_address: bool
    has_suspicious_tld: bool
    findings: list[str]


class AnalyzeDomainIndicatorsUseCase:
    def execute(
        self,
        command: AnalyzeDomainIndicatorsCommand,
    ) -> DomainIndicatorsAnalysis:
        domain = command.domain
        domain_contains_punycode = contains_punycode(domain)
        domain_has_mixed_scripts = contains_mixed_scripts(domain)
        domain_has_confusable_characters = contains_confusable_characters(domain)
        domain_has_suspicious_subdomain_depth = has_suspicious_subdomain_depth(
            domain,
            max_depth=command.max_subdomain_depth,
        )
        domain_looks_like_ip_address = looks_like_ip_address_host(domain)
        domain_has_suspicious_tld = has_suspicious_tld(
            domain,
            command.suspicious_tlds,
        )
        confusable_characters = find_confusable_characters(domain)
        findings: list[str] = []

        if domain_contains_punycode:
            findings.append(DOMAIN_CONTAINS_PUNYCODE)

        if domain_has_mixed_scripts:
            findings.append(DOMAIN_HAS_MIXED_SCRIPTS)

        if domain_has_confusable_characters:
            findings.append(DOMAIN_HAS_CONFUSABLE_CHARACTERS)

        if domain_has_suspicious_subdomain_depth:
            findings.append(DOMAIN_HAS_SUSPICIOUS_DEPTH)

        if domain_looks_like_ip_address:
            findings.append(DOMAIN_LOOKS_LIKE_IP_ADDRESS)

        if domain_has_suspicious_tld:
            findings.append(DOMAIN_HAS_SUSPICIOUS_TLD)

        return DomainIndicatorsAnalysis(
            domain=domain,
            labels=split_domain_labels(domain),
            scripts=detect_unicode_scripts(domain),
            contains_punycode=domain_contains_punycode,
            has_mixed_scripts=domain_has_mixed_scripts,
            has_confusable_characters=domain_has_confusable_characters,
            confusable_characters=confusable_characters,
            has_suspicious_subdomain_depth=domain_has_suspicious_subdomain_depth,
            looks_like_ip_address=domain_looks_like_ip_address,
            has_suspicious_tld=domain_has_suspicious_tld,
            findings=findings,
        )
