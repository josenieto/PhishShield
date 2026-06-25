from dataclasses import dataclass
from urllib.parse import parse_qsl, urlsplit

from domain.services.url_analysis.credentials import has_embedded_credentials
from domain.services.url_analysis.query import has_suspicious_query_density
from domain.services.url_analysis.schemes import (
    is_suspicious_url_scheme,
    is_url_scheme_allowed,
)
from domain.services.url_analysis.shorteners import has_url_shortener_domain


URL_SCHEME_NOT_ALLOWED = "URL_SCHEME_NOT_ALLOWED"
URL_HAS_SUSPICIOUS_SCHEME = "URL_HAS_SUSPICIOUS_SCHEME"
URL_HAS_EMBEDDED_CREDENTIALS = "URL_HAS_EMBEDDED_CREDENTIALS"
URL_HAS_SUSPICIOUS_QUERY_DENSITY = "URL_HAS_SUSPICIOUS_QUERY_DENSITY"
URL_USES_KNOWN_SHORTENER_DOMAIN = "URL_USES_KNOWN_SHORTENER_DOMAIN"


@dataclass(frozen=True)
class AnalyzeUrlIndicatorsCommand:
    url: str
    allowed_schemes: set[str]
    known_shorteners: set[str]
    query_density_threshold: int = 3


@dataclass(frozen=True)
class UrlIndicatorsAnalysis:
    url: str
    scheme: str
    domain: str
    query_parameter_count: int
    is_scheme_allowed: bool
    has_suspicious_scheme: bool
    has_embedded_credentials: bool
    has_suspicious_query_density: bool
    uses_known_shortener_domain: bool
    findings: list[str]


class AnalyzeUrlIndicatorsUseCase:
    def execute(
        self,
        command: AnalyzeUrlIndicatorsCommand,
    ) -> UrlIndicatorsAnalysis:
        url = command.url
        scheme, domain, query_parameter_count = _parse_url_indicators(url)
        url_scheme_allowed = is_url_scheme_allowed(scheme, command.allowed_schemes)
        url_has_suspicious_scheme = is_suspicious_url_scheme(scheme)
        url_has_embedded_credentials = has_embedded_credentials(url)
        url_has_suspicious_query_density = has_suspicious_query_density(
            url,
            command.query_density_threshold,
        )
        url_uses_known_shortener_domain = has_url_shortener_domain(
            domain,
            command.known_shorteners,
        )
        finding_conditions = [
            (not url_scheme_allowed, URL_SCHEME_NOT_ALLOWED),
            (url_has_suspicious_scheme, URL_HAS_SUSPICIOUS_SCHEME),
            (url_has_embedded_credentials, URL_HAS_EMBEDDED_CREDENTIALS),
            (url_has_suspicious_query_density, URL_HAS_SUSPICIOUS_QUERY_DENSITY),
            (url_uses_known_shortener_domain, URL_USES_KNOWN_SHORTENER_DOMAIN),
        ]
        findings = [
            finding
            for condition, finding in finding_conditions
            if condition
        ]

        return UrlIndicatorsAnalysis(
            url=url,
            scheme=scheme,
            domain=domain,
            query_parameter_count=query_parameter_count,
            is_scheme_allowed=url_scheme_allowed,
            has_suspicious_scheme=url_has_suspicious_scheme,
            has_embedded_credentials=url_has_embedded_credentials,
            has_suspicious_query_density=url_has_suspicious_query_density,
            uses_known_shortener_domain=url_uses_known_shortener_domain,
            findings=findings,
        )


def _parse_url_indicators(url: str) -> tuple[str, str, int]:
    try:
        parsed_url = urlsplit(url)
        query_parameter_count = len(
            parse_qsl(parsed_url.query, keep_blank_values=True)
        )
    except ValueError:
        return "", "", 0

    return parsed_url.scheme, parsed_url.hostname or "", query_parameter_count
