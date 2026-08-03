import json
from pathlib import Path

import pytest

from tools.ml_data_preparation.prepare_ceas_08 import prepare_ceas_08_csv


def test_should_prepare_ceas_rows_without_using_audit_metadata_as_features(tmp_path: Path) -> None:
    input_file = tmp_path / "CEAS_08.csv"
    output_file = tmp_path / "prepared.jsonl"
    input_file.write_text(
        "sender,receiver,date,subject,body,label,urls\n"
        "Alice <alice@example.com>,bob@example.com,2020-01-01,Account notice,Please review https://example.com,0,1\n"
        "Evil <evil@example.test>,bob@example.com,2020-01-02,Verify account,Verify your account now,1,0\n",
        encoding="utf-8",
    )

    summary = prepare_ceas_08_csv(input_file, output_file, {"0": "benign", "1": "suspicious"})
    rows = [json.loads(line) for line in output_file.read_text(encoding="utf-8").splitlines()]

    assert summary.processed == 2
    assert summary.labels == {"benign": 1, "suspicious": 1}
    assert rows[0]["sender_domain"] == "example.com"
    assert rows[0]["urls"] == ["https://example.com"]
    assert rows[0]["metadata"]["receiver"] == "bob@example.com"
    assert rows[0]["metadata"]["date"] == "2020-01-01"
    assert rows[0]["attachment_filenames"] == []


def test_should_count_duplicate_and_empty_ceas_rows(tmp_path: Path) -> None:
    input_file = tmp_path / "CEAS_08.csv"
    output_file = tmp_path / "prepared.jsonl"
    input_file.write_text(
        "sender,receiver,date,subject,body,label,urls\n"
        "a@example.com,b@example.com,2020-01-01,,Body,0,0\n"
        "a@example.com,b@example.com,2020-01-01,,Body,0,0\n",
        encoding="utf-8",
    )

    summary = prepare_ceas_08_csv(input_file, output_file, {"0": "benign", "1": "suspicious"})

    assert summary.empty_subject == 2
    assert summary.duplicate_content == 1


def test_should_reject_unknown_ceas_label(tmp_path: Path) -> None:
    input_file = tmp_path / "CEAS_08.csv"
    input_file.write_text(
        "sender,receiver,date,subject,body,label,urls\n"
        "a@example.com,b@example.com,2020-01-01,Subject,Body,2,0\n",
        encoding="utf-8",
    )

    with pytest.raises(AssertionError):
        summary = prepare_ceas_08_csv(input_file, tmp_path / "prepared.jsonl", {"0": "benign", "1": "suspicious"})
        assert summary.unsupported_label == 0
