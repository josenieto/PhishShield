import json
from pathlib import Path

import pytest

from tools.ml_data_preparation.prepare_spamassassin import (
    main,
    prepare_spamassassin_directory,
)


def test_should_prepare_spamassassin_directory_to_jsonl(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_path = tmp_path / "prepared" / "easy_ham.jsonl"
    (input_dir / "0001.eml").write_bytes(_sample_email_bytes("First message", "https://example.com/one"))
    (input_dir / "0002.eml").write_bytes(_sample_email_bytes("Second message", "https://example.com/two"))

    summary = prepare_spamassassin_directory(
        input_dir=input_dir,
        label="easy_ham",
        output_path=output_path,
    )

    rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

    assert summary.processed == 2
    assert summary.failed == 0
    assert summary.empty_subject == 0
    assert summary.empty_body == 0
    assert summary.urls_found == 2
    assert rows[0]["source"] == "spamassassin"
    assert rows[0]["source_id"] == "0001.eml"
    assert rows[0]["original_label"] == "easy_ham"
    assert rows[0]["normalized_label"] == "benign"
    assert rows[0]["subject"] == "First message"
    assert rows[0]["urls"] == ["https://example.com/one"]
    assert rows[0]["metadata"] == {"original_label": "easy_ham"}


def test_should_respect_processing_limit(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_path = tmp_path / "prepared" / "spam.jsonl"
    (input_dir / "0001.eml").write_bytes(_sample_email_bytes("First message", "https://example.com/one"))
    (input_dir / "0002.eml").write_bytes(_sample_email_bytes("Second message", "https://example.com/two"))

    summary = prepare_spamassassin_directory(
        input_dir=input_dir,
        label="spam",
        output_path=output_path,
        limit=1,
    )

    rows = output_path.read_text(encoding="utf-8").splitlines()

    assert summary.processed == 1
    assert summary.failed == 0
    assert len(rows) == 1
    assert json.loads(rows[0])["normalized_label"] == "suspicious"


def test_should_escape_unicode_line_separators_for_jsonl_output(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_path = tmp_path / "prepared" / "spam.jsonl"
    (input_dir / "0001.eml").write_bytes(
        _sample_email_bytes("First message", "https://example.com/one", body_prefix="Line one\u2028Line two")
    )

    summary = prepare_spamassassin_directory(
        input_dir=input_dir,
        label="spam",
        output_path=output_path,
    )
    output_text = output_path.read_text(encoding="utf-8")

    assert summary.processed == 1
    assert "\\u2028" in output_text
    assert len(output_text.splitlines()) == 1
    assert json.loads(output_text)["body_text"] == "Line one\u2028Line two at https://example.com/one."


def test_should_continue_after_failed_file(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_path = tmp_path / "prepared" / "easy_ham.jsonl"
    (input_dir / "0001.eml").write_bytes(_sample_email_bytes("First message", "https://example.com/one"))

    summary = prepare_spamassassin_directory(
        input_dir=input_dir,
        label="unknown_label",
        output_path=output_path,
    )

    assert summary.processed == 0
    assert summary.failed == 1
    assert output_path.read_text(encoding="utf-8") == ""


def test_should_reject_negative_limit(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    with pytest.raises(ValueError, match="limit must be greater than or equal to zero"):
        prepare_spamassassin_directory(
            input_dir=input_dir,
            label="easy_ham",
            output_path=tmp_path / "output.jsonl",
            limit=-1,
        )


def test_should_return_non_zero_from_cli_when_files_fail(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "0001.eml").write_bytes(_sample_email_bytes("First message", "https://example.com/one"))

    exit_code = main([
        "--input-dir",
        str(input_dir),
        "--label",
        "unknown_label",
        "--output",
        str(tmp_path / "output.jsonl"),
    ])

    assert exit_code == 1


def _sample_email_bytes(subject: str, url: str, body_prefix: str = "Please review your account summary") -> bytes:
    return "\r\n".join(
        [
            "From: Product Team <updates@example.com>",
            f"Subject: {subject}",
            "Content-Type: text/plain; charset=utf-8",
            "",
            f"{body_prefix} at {url}.",
        ]
    ).encode("utf-8")
