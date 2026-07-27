import json
from pathlib import Path

import pytest

from tools.ml_data_preparation.prepare_phishing_email_detection import (
    main,
    prepare_phishing_email_detection_csv,
)


def test_should_prepare_phishing_email_detection_csv_to_jsonl(tmp_path: Path) -> None:
    input_file = tmp_path / "Phishing_Email.csv"
    output_path = tmp_path / "prepared" / "phishing_email_detection.jsonl"
    input_file.write_text(
        _csv_text(
            [
                ["1", "Your account summary is ready at https://example.com/summary.", "Safe Email"],
                ["2", "Urgent: verify your password at https://example.net/login.", "Phishing Email"],
            ]
        ),
        encoding="utf-8",
    )

    summary = prepare_phishing_email_detection_csv(
        input_file=input_file,
        output_path=output_path,
    )
    rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

    assert summary.rows_read == 2
    assert summary.processed == 2
    assert summary.failed == 0
    assert summary.skipped_empty_text == 0
    assert summary.unsupported_label == 0
    assert summary.urls_found == 2
    assert summary.labels == {"benign": 1, "suspicious": 1}
    assert summary.phishing_keyword_hits["account"] == 1
    assert summary.phishing_keyword_hits["password"] == 1
    assert rows[0]["source"] == "phishing_email_detection"
    assert rows[0]["source_id"] == "csv-1"
    assert rows[0]["original_label"] == "Safe Email"
    assert rows[0]["normalized_label"] == "benign"
    assert rows[0]["subject"] == ""
    assert rows[0]["body_text"] == "Your account summary is ready at https://example.com/summary."
    assert rows[0]["raw_available"] is False
    assert rows[0]["metadata"] == {"original_label": "Safe Email", "csv_row_number": "2"}


def test_should_skip_empty_text_rows(tmp_path: Path) -> None:
    input_file = tmp_path / "Phishing_Email.csv"
    output_path = tmp_path / "prepared" / "phishing_email_detection.jsonl"
    input_file.write_text(
        _csv_text(
            [
                ["1", "", "Phishing Email"],
                ["2", "Safe notification.", "Safe Email"],
            ]
        ),
        encoding="utf-8",
    )

    summary = prepare_phishing_email_detection_csv(
        input_file=input_file,
        output_path=output_path,
    )
    rows = output_path.read_text(encoding="utf-8").splitlines()

    assert summary.rows_read == 2
    assert summary.processed == 1
    assert summary.skipped_empty_text == 1
    assert len(rows) == 1


def test_should_report_duplicate_and_quality_counters(tmp_path: Path) -> None:
    input_file = tmp_path / "Phishing_Email.csv"
    output_path = tmp_path / "prepared" / "phishing_email_detection.jsonl"
    input_file.write_text(
        _csv_text(
            [
                ["1", "https://example.com", "Safe Email"],
                ["2", "https://example.com", "Safe Email"],
                ["3", "Buy adult stock investment newsletter now", "Phishing Email"],
                ["4", "short", "Phishing Email"],
                ["5", "x" * 10001, "Phishing Email"],
            ]
        ),
        encoding="utf-8",
    )

    summary = prepare_phishing_email_detection_csv(
        input_file=input_file,
        output_path=output_path,
    )

    assert summary.processed == 5
    assert summary.duplicate_text == 1
    assert summary.url_only_rows == 2
    assert summary.short_rows_lt_30 == 3
    assert summary.long_rows_gt_10000 == 1
    assert summary.spam_keyword_hits["adult"] == 1
    assert summary.spam_keyword_hits["stock"] == 1
    assert summary.spam_keyword_hits["investment"] == 1
    assert summary.spam_keyword_hits["newsletter"] == 1


def test_should_report_unsupported_labels_without_failing_other_rows(tmp_path: Path) -> None:
    input_file = tmp_path / "Phishing_Email.csv"
    output_path = tmp_path / "prepared" / "phishing_email_detection.jsonl"
    input_file.write_text(
        _csv_text(
            [
                ["1", "Unsupported label row.", "Spam Email"],
                ["2", "Verify your account.", "Phishing Email"],
            ]
        ),
        encoding="utf-8",
    )

    summary = prepare_phishing_email_detection_csv(
        input_file=input_file,
        output_path=output_path,
    )
    rows = output_path.read_text(encoding="utf-8").splitlines()

    assert summary.rows_read == 2
    assert summary.processed == 1
    assert summary.unsupported_label == 1
    assert len(rows) == 1


def test_should_respect_processing_limit(tmp_path: Path) -> None:
    input_file = tmp_path / "Phishing_Email.csv"
    output_path = tmp_path / "prepared" / "phishing_email_detection.jsonl"
    input_file.write_text(
        _csv_text(
            [
                ["1", "First safe email.", "Safe Email"],
                ["2", "Second phishing email.", "Phishing Email"],
            ]
        ),
        encoding="utf-8",
    )

    summary = prepare_phishing_email_detection_csv(
        input_file=input_file,
        output_path=output_path,
        limit=1,
    )
    rows = output_path.read_text(encoding="utf-8").splitlines()

    assert summary.rows_read == 1
    assert summary.processed == 1
    assert len(rows) == 1


def test_should_reject_negative_limit(tmp_path: Path) -> None:
    input_file = tmp_path / "Phishing_Email.csv"
    input_file.write_text(_csv_text([["1", "Safe email.", "Safe Email"]]), encoding="utf-8")

    with pytest.raises(ValueError, match="limit must be greater than or equal to zero"):
        prepare_phishing_email_detection_csv(
            input_file=input_file,
            output_path=tmp_path / "output.jsonl",
            limit=-1,
        )


def test_should_reject_missing_required_columns(tmp_path: Path) -> None:
    input_file = tmp_path / "Phishing_Email.csv"
    input_file.write_text("id,text,label\n1,body,Safe Email\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required columns"):
        prepare_phishing_email_detection_csv(
            input_file=input_file,
            output_path=tmp_path / "output.jsonl",
        )


def test_should_return_non_zero_from_cli_when_labels_are_unsupported(tmp_path: Path) -> None:
    input_file = tmp_path / "Phishing_Email.csv"
    output_path = tmp_path / "prepared" / "phishing_email_detection.jsonl"
    input_file.write_text(_csv_text([["1", "Unsupported label row.", "Spam Email"]]), encoding="utf-8")

    exit_code = main([
        "--input-file",
        str(input_file),
        "--output",
        str(output_path),
    ])

    assert exit_code == 1


def _csv_text(rows: list[list[str]]) -> str:
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["", "Email Text", "Email Type"])
    writer.writerows(rows)
    return output.getvalue()
