import json
from pathlib import Path

import pytest

from tools.ml_data_preparation.prepare_enron import main, prepare_enron_directory


def test_should_prepare_capped_enron_directory_to_jsonl(tmp_path: Path) -> None:
    input_dir = tmp_path / "maildir"
    output_path = tmp_path / "prepared" / "enron.jsonl"
    _write_maildir(
        input_dir,
        {
            "user-a/inbox/001": _sample_email_bytes("Project update", "Please review https://example.com/doc."),
            "user-b/sent/002": _sample_email_bytes("Meeting notes", "Meeting notes are ready."),
        },
    )

    summary = prepare_enron_directory(
        input_dir=input_dir,
        output_path=output_path,
        limit=1,
    )
    rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

    assert summary.discovered_files == 1
    assert summary.processed == 1
    assert summary.failed == 0
    assert summary.skipped_empty_body == 0
    assert summary.urls_found == 1
    assert summary.users == {"user-a": 1}
    assert summary.folders == {"inbox": 1}
    assert rows[0]["source"] == "enron"
    assert rows[0]["source_id"] == "user-a/inbox/001"
    assert rows[0]["original_label"] == "benign"
    assert rows[0]["normalized_label"] == "benign"
    assert rows[0]["subject"] == "Project update"
    assert rows[0]["urls"] == ["https://example.com/doc"]
    assert rows[0]["metadata"] == {
        "folder": "inbox",
        "mailbox_user": "user-a",
        "original_label": "benign",
        "relative_path": "user-a/inbox/001",
    }


def test_should_skip_empty_body_and_report_duplicates(tmp_path: Path) -> None:
    input_dir = tmp_path / "maildir"
    output_path = tmp_path / "prepared" / "enron.jsonl"
    duplicate_body = "Repeated body."
    _write_maildir(
        input_dir,
        {
            "user-a/inbox/001": _sample_email_bytes("First", duplicate_body),
            "user-a/inbox/002": _sample_email_bytes("Second", duplicate_body),
            "user-a/inbox/003": _sample_email_bytes("Empty", ""),
        },
    )

    summary = prepare_enron_directory(
        input_dir=input_dir,
        output_path=output_path,
        limit=None,
    )
    rows = output_path.read_text(encoding="utf-8").splitlines()

    assert summary.discovered_files == 3
    assert summary.processed == 2
    assert summary.skipped_empty_body == 1
    assert summary.duplicate_body == 1
    assert summary.duplicate_subject_body == 0
    assert len(rows) == 2


def test_should_reject_negative_limit(tmp_path: Path) -> None:
    input_dir = tmp_path / "maildir"
    _write_maildir(input_dir, {"user-a/inbox/001": _sample_email_bytes("Subject", "Body")})

    with pytest.raises(ValueError, match="limit must be greater than or equal to zero"):
        prepare_enron_directory(
            input_dir=input_dir,
            output_path=tmp_path / "output.jsonl",
            limit=-1,
        )


def test_should_return_zero_from_cli_when_preparation_succeeds(tmp_path: Path) -> None:
    input_dir = tmp_path / "maildir"
    output_path = tmp_path / "prepared" / "enron.jsonl"
    _write_maildir(input_dir, {"user-a/inbox/001": _sample_email_bytes("Subject", "Body")})

    exit_code = main([
        "--input-dir",
        str(input_dir),
        "--output",
        str(output_path),
        "--limit",
        "1",
    ])

    assert exit_code == 0


def _write_maildir(input_dir: Path, files: dict[str, bytes]) -> None:
    for name, content in files.items():
        email_path = input_dir / Path(name)
        email_path.parent.mkdir(parents=True, exist_ok=True)
        email_path.write_bytes(content)


def _sample_email_bytes(subject: str, body: str) -> bytes:
    return "\r\n".join(
        [
            "From: Project Team <project@example.com>",
            f"Subject: {subject}",
            "Content-Type: text/plain; charset=utf-8",
            "",
            body,
        ]
    ).encode("utf-8")
