import json
from pathlib import Path

from tools.ml_data_preparation.validate_prepared_dataset import (
    main,
    validate_prepared_datasets,
)


def test_should_validate_prepared_jsonl_dataset(tmp_path: Path) -> None:
    input_path = tmp_path / "prepared.jsonl"
    input_path.write_text(
        _jsonl_row(sample_id="sample-1", normalized_label="benign")
        + _jsonl_row(sample_id="sample-2", normalized_label="suspicious", urls=["https://example.com"]),
        encoding="utf-8",
    )

    summary = validate_prepared_datasets([input_path])

    assert summary.is_valid is True
    assert summary.files == 1
    assert summary.rows == 2
    assert summary.invalid_rows == 0
    assert summary.duplicate_sample_ids == 0
    assert summary.labels == {"benign": 1, "suspicious": 1}
    assert summary.urls_found == 1


def test_should_report_missing_required_fields(tmp_path: Path) -> None:
    input_path = tmp_path / "prepared.jsonl"
    input_path.write_text('{"sample_id": "sample-1"}\n', encoding="utf-8")

    summary = validate_prepared_datasets([input_path])

    assert summary.is_valid is False
    assert summary.invalid_rows == 1
    assert "missing required fields" in summary.errors[0]


def test_should_report_invalid_json_rows(tmp_path: Path) -> None:
    input_path = tmp_path / "prepared.jsonl"
    input_path.write_text("not-json\n", encoding="utf-8")

    summary = validate_prepared_datasets([input_path])

    assert summary.is_valid is False
    assert summary.invalid_rows == 1
    assert "invalid JSON" in summary.errors[0]


def test_should_not_split_json_rows_on_unicode_line_separators(tmp_path: Path) -> None:
    input_path = tmp_path / "prepared.jsonl"
    input_path.write_text(
        _jsonl_row(
            sample_id="sample-1",
            normalized_label="benign",
            body_text="Line one\u2028Line two",
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    summary = validate_prepared_datasets([input_path])

    assert summary.is_valid is True
    assert summary.rows == 1
    assert summary.invalid_rows == 0
    assert summary.labels == {"benign": 1}


def test_should_report_duplicate_sample_ids(tmp_path: Path) -> None:
    input_path = tmp_path / "prepared.jsonl"
    input_path.write_text(
        _jsonl_row(sample_id="sample-1", normalized_label="benign")
        + _jsonl_row(sample_id="sample-1", normalized_label="suspicious"),
        encoding="utf-8",
    )

    summary = validate_prepared_datasets([input_path])

    assert summary.is_valid is False
    assert summary.duplicate_sample_ids == 1
    assert any("duplicate sample_id" in error for error in summary.errors)


def test_should_report_invalid_label(tmp_path: Path) -> None:
    input_path = tmp_path / "prepared.jsonl"
    input_path.write_text(
        _jsonl_row(sample_id="sample-1", normalized_label="invalid"),
        encoding="utf-8",
    )

    summary = validate_prepared_datasets([input_path])

    assert summary.is_valid is False
    assert summary.invalid_rows == 1
    assert any("invalid normalized_label" in error for error in summary.errors)


def test_should_combine_multiple_input_files(tmp_path: Path) -> None:
    first_input = tmp_path / "first.jsonl"
    second_input = tmp_path / "second.jsonl"
    first_input.write_text(_jsonl_row(sample_id="sample-1", normalized_label="benign"), encoding="utf-8")
    second_input.write_text(_jsonl_row(sample_id="sample-2", normalized_label="suspicious"), encoding="utf-8")

    summary = validate_prepared_datasets([first_input, second_input])

    assert summary.is_valid is True
    assert summary.files == 2
    assert summary.rows == 2
    assert summary.labels == {"benign": 1, "suspicious": 1}


def test_should_return_non_zero_exit_code_for_invalid_dataset(tmp_path: Path) -> None:
    input_path = tmp_path / "prepared.jsonl"
    input_path.write_text("not-json\n", encoding="utf-8")

    exit_code = main(["--input", str(input_path)])

    assert exit_code == 1


def _jsonl_row(
    sample_id: str,
    normalized_label: str,
    urls: list[str] | None = None,
    body_text: str = "Body",
    ensure_ascii: bool = True,
) -> str:
    return json.dumps(
        {
            "sample_id": sample_id,
            "source": "spamassassin",
            "source_id": f"{sample_id}.eml",
            "source_uri": "https://spamassassin.apache.org/old/publiccorpus/",
            "original_label": normalized_label,
            "normalized_label": normalized_label,
            "subject": "Subject",
            "body_text": body_text,
            "sender_domain": "example.com",
            "urls": [] if urls is None else urls,
            "attachment_filenames": [],
            "raw_available": True,
            "metadata": {"original_label": normalized_label},
        },
        ensure_ascii=ensure_ascii,
        sort_keys=True,
    ) + "\n"
