from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCORING_SENSITIVE_PREFIXES = (
    "src/domain/services/finding_analysis/",
    "src/domain/services/risk_scoring/",
    "src/domain/services/social_engineering/",
)
SCORING_SENSITIVE_FILES = {
    "src/application/use_cases/analyze_social_engineering_indicators.py",
    "src/application/use_cases/calculate_risk_score.py",
    "src/domain/value_objects/finding.py",
    "src/infrastructure/config/analysis_defaults.py",
}


def _normalized_path(file_path: str) -> str:
    return Path(file_path).as_posix()


def _is_scoring_sensitive(file_path: str) -> bool:
    normalized_path = _normalized_path(file_path)

    return normalized_path in SCORING_SENSITIVE_FILES or normalized_path.startswith(
        SCORING_SENSITIVE_PREFIXES,
    )


def _staged_paths() -> list[str]:
    completed_process = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        check=True,
        capture_output=True,
        text=True,
    )

    return [
        _normalized_path(file_path)
        for file_path in completed_process.stdout.splitlines()
        if file_path.strip()
    ]


def main() -> int:
    changed_paths = _staged_paths()
    scoring_sensitive_paths = [file_path for file_path in changed_paths if _is_scoring_sensitive(file_path)]

    if not scoring_sensitive_paths:
        return 0

    has_test_change = any(file_path.startswith("tests/") for file_path in changed_paths)
    has_calibration_doc_change = "doc/SCORING_CALIBRATION.md" in changed_paths

    if has_test_change and has_calibration_doc_change:
        return 0

    print("Scoring-sensitive changes require both fixture/test evidence and calibration documentation updates.")
    print("Changed scoring-sensitive paths:")
    for file_path in scoring_sensitive_paths:
        print(f"- {file_path}")

    if not has_test_change:
        print("Missing required evidence update under tests/.")

    if not has_calibration_doc_change:
        print("Missing required update to doc/SCORING_CALIBRATION.md.")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
