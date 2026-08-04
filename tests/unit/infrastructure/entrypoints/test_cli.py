import json
from pathlib import Path

from infrastructure.entrypoints.cli import (
    EXIT_ANALYSIS_ERROR,
    EXIT_FILE_ERROR,
    EXIT_OK,
    EXIT_THRESHOLD_REACHED,
    main,
)


def test_should_print_json_and_return_zero_for_benign_fixture(capsys) -> None:
    result = main(["analyze", "tests/fixtures/emails/benign_account_summary.eml", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert result == EXIT_OK
    assert payload["risk_score"]["risk_level"] == "LOW"
    assert "finding_codes" in payload


def test_should_return_one_when_fail_threshold_is_reached(capsys) -> None:
    result = main([
        "analyze",
        "tests/fixtures/emails/suspicious_html_notice.eml",
        "--format",
        "json",
        "--fail-on",
        "high",
    ])

    assert result == EXIT_THRESHOLD_REACHED
    assert capsys.readouterr().out


def test_should_return_file_error_for_missing_email(capsys) -> None:
    result = main(["analyze", "missing-email.eml"])

    assert result == EXIT_FILE_ERROR
    assert "Unable to read email file" in capsys.readouterr().err


def test_should_return_analysis_error_for_oversized_email(tmp_path: Path, capsys) -> None:
    path = tmp_path / "oversized.eml"
    path.write_bytes(b"x" * 1_000_001)

    result = main(["analyze", str(path)])

    assert result == EXIT_ANALYSIS_ERROR
    assert "maximum allowed size" in capsys.readouterr().err
