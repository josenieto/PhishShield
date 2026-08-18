"""Command-line entrypoint for deterministic PhishShield analysis."""

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from application.use_cases.analyze_raw_email import AnalyzeRawEmailCommand, AnalyzeRawEmailUseCase
from infrastructure.adapters.email_parser.python_email_content_extractor import PythonEmailContentExtractorAdapter
from infrastructure.config.analysis_defaults import (
    DEFAULT_ALLOWED_URL_SCHEMES,
    DEFAULT_CREDENTIAL_REQUEST_TERMS,
    DEFAULT_CRITICAL_INDICATORS,
    DEFAULT_FINDING_WEIGHTS,
    DEFAULT_FINANCIAL_PRESSURE_TERMS,
    DEFAULT_KNOWN_SHORTENERS,
    DEFAULT_SUSPICIOUS_TLDS,
    DEFAULT_URGENCY_TERMS,
)
from infrastructure.config.api_defaults import load_api_settings
from infrastructure.entrypoints.api.schemas.analyze_email import extracted_email_analysis_to_response
from infrastructure.entrypoints.upload_limits import UploadSizeLimitExceeded, enforce_upload_size


EXIT_OK = 0
EXIT_THRESHOLD_REACHED = 1
EXIT_USAGE_ERROR = 2
EXIT_FILE_ERROR = 3
EXIT_ANALYSIS_ERROR = 4

_RISK_LEVELS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    email_path = Path(args.email_path)
    try:
        email_bytes = email_path.read_bytes()
    except (OSError, ValueError) as exc:
        print(f"Unable to read email file: {exc}", file=sys.stderr)
        return EXIT_FILE_ERROR

    try:
        enforce_upload_size(email_bytes, load_api_settings().max_upload_bytes)
    except UploadSizeLimitExceeded:
        print("Email file exceeds the maximum allowed size.", file=sys.stderr)
        return EXIT_ANALYSIS_ERROR

    try:
        analysis = _build_use_case().execute(
            AnalyzeRawEmailCommand(
                email_bytes=email_bytes,
                suspicious_tlds=DEFAULT_SUSPICIOUS_TLDS,
                allowed_url_schemes=DEFAULT_ALLOWED_URL_SCHEMES,
                known_shorteners=DEFAULT_KNOWN_SHORTENERS,
                urgency_terms=DEFAULT_URGENCY_TERMS,
                financial_pressure_terms=DEFAULT_FINANCIAL_PRESSURE_TERMS,
                credential_request_terms=DEFAULT_CREDENTIAL_REQUEST_TERMS,
                finding_weights=DEFAULT_FINDING_WEIGHTS,
                critical_indicators=DEFAULT_CRITICAL_INDICATORS,
            )
        )
    except Exception as exc:
        print(f"Email could not be analyzed: {exc}", file=sys.stderr)
        return EXIT_ANALYSIS_ERROR

    response = extracted_email_analysis_to_response(analysis)
    if args.format == "json":
        print(json.dumps(response.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        _print_text_result(response.model_dump(mode="json"))

    return (
        EXIT_THRESHOLD_REACHED
        if _threshold_reached(response.risk_score.risk_level, args.fail_on)
        else EXIT_OK
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phishshield",
        description="Run deterministic PhishShield triage on one .eml file.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze = subparsers.add_parser("analyze", help="Analyze one .eml file.")
    analyze.add_argument("email_path", help="Path to the .eml file.")
    analyze.add_argument("--format", choices=("text", "json"), default="text")
    analyze.add_argument("--fail-on", choices=("none", "low", "medium", "high", "critical"), default="none")
    return parser


def _build_use_case() -> AnalyzeRawEmailUseCase:
    return AnalyzeRawEmailUseCase(PythonEmailContentExtractorAdapter())


def _threshold_reached(risk_level: str, fail_on: str) -> bool:
    if fail_on == "none":
        return False
    return _RISK_LEVELS.index(risk_level.upper()) >= _RISK_LEVELS.index(fail_on.upper())


def _print_text_result(payload: dict[str, object]) -> None:
    risk_score = payload["risk_score"]
    summary = payload["finding_summary"]
    evidence = payload["extracted_evidence"]
    print(f"Risk level: {risk_score['risk_level']}")
    print(f"Risk score: {risk_score['capped_score']}/100")
    print(f"Subject: {evidence['subject']}")
    print(f"Sender domain: {evidence['sender_domain']}")
    print(f"Findings: {summary['total_findings']}")
    for finding in summary["sorted_findings"]:
        print(f"- [{finding['severity']}] {finding['code']}: {finding['explanation']}")


if __name__ == "__main__":
    raise SystemExit(main())
