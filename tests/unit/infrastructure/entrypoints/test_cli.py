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


def test_should_return_analysis_error_for_oversized_email(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    monkeypatch.setenv("PHISHSHIELD_MAX_UPLOAD_BYTES", "5")
    path = tmp_path / "oversized.eml"
    path.write_bytes(b"x" * 6)

    result = main(["analyze", str(path)])

    assert result == EXIT_ANALYSIS_ERROR
    assert "maximum allowed size" in capsys.readouterr().err


def test_should_render_human_readable_text(capsys) -> None:
    result = main(["analyze", "tests/fixtures/emails/benign_account_summary.eml"])

    captured = capsys.readouterr()
    assert result == EXIT_OK
    assert "Risk level: LOW" in captured.out
    assert "Subject:" in captured.out


def test_should_return_analysis_error_when_analysis_fails(monkeypatch, tmp_path: Path, capsys) -> None:
    path = tmp_path / "email.eml"
    path.write_bytes(b"From: sender@example.com\n\nBody")

    class FailingUseCase:
        def execute(self, command):
            raise ValueError("analysis failed")

    monkeypatch.setattr("infrastructure.entrypoints.cli._build_use_case", lambda: FailingUseCase())

    result = main(["analyze", str(path)])

    assert result == EXIT_ANALYSIS_ERROR
    assert "Email could not be analyzed" in capsys.readouterr().err
