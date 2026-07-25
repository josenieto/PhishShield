import json
from pathlib import Path

import pytest

from tools.ml_data_preparation.prepare_fraudulent_email_corpus import (
    main,
    prepare_fraudulent_email_corpus_file,
)


def test_should_prepare_fraudulent_email_corpus_file_to_jsonl(tmp_path: Path) -> None:
    input_file = tmp_path / "fradulent_emails.txt"
    output_path = tmp_path / "prepared" / "fraudulent.jsonl"
    input_file.write_text(_sample_corpus_text(), encoding="utf-8")

    summary = prepare_fraudulent_email_corpus_file(
        input_file=input_file,
        output_path=output_path,
    )
    rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

    assert summary.discovered == 2
    assert summary.processed == 2
    assert summary.failed == 0
    assert summary.empty_subject == 0
    assert summary.empty_body == 0
    assert summary.urls_found == 2
    assert rows[0]["source"] == "fraudulent_email_corpus"
    assert rows[0]["source_id"] == "message-00001"
    assert rows[0]["original_label"] == "fraud"
    assert rows[0]["normalized_label"] == "suspicious"
    assert rows[0]["subject"] == "First proposal"
    assert rows[0]["urls"] == ["https://example.net/reply"]
    assert rows[0]["metadata"] == {"original_label": "fraud"}


def test_should_prepare_corpus_file_without_utf8_replacement_decoding(tmp_path: Path) -> None:
    input_file = tmp_path / "fradulent_emails.txt"
    output_path = tmp_path / "prepared" / "fraudulent.jsonl"
    input_file.write_bytes(_latin1_sample_message_bytes())

    summary = prepare_fraudulent_email_corpus_file(
        input_file=input_file,
        output_path=output_path,
    )
    rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

    assert summary.discovered == 1
    assert summary.processed == 1
    assert rows[0]["subject"] == "Oferta especial"
    assert rows[0]["body_text"] == "Transferencia especial para caf\u00e9."


def test_should_respect_processing_limit(tmp_path: Path) -> None:
    input_file = tmp_path / "fradulent_emails.txt"
    output_path = tmp_path / "prepared" / "fraudulent.jsonl"
    input_file.write_text(_sample_corpus_text(), encoding="utf-8")

    summary = prepare_fraudulent_email_corpus_file(
        input_file=input_file,
        output_path=output_path,
        limit=1,
    )
    rows = output_path.read_text(encoding="utf-8").splitlines()

    assert summary.discovered == 2
    assert summary.processed == 1
    assert summary.failed == 0
    assert len(rows) == 1


def test_should_reject_negative_limit(tmp_path: Path) -> None:
    input_file = tmp_path / "fradulent_emails.txt"
    input_file.write_text(_sample_corpus_text(), encoding="utf-8")

    with pytest.raises(ValueError, match="limit must be greater than or equal to zero"):
        prepare_fraudulent_email_corpus_file(
            input_file=input_file,
            output_path=tmp_path / "output.jsonl",
            limit=-1,
        )


def test_should_return_zero_from_cli_when_preparation_succeeds(tmp_path: Path) -> None:
    input_file = tmp_path / "fradulent_emails.txt"
    output_path = tmp_path / "prepared" / "fraudulent.jsonl"
    input_file.write_text(_sample_corpus_text(), encoding="utf-8")

    exit_code = main([
        "--input-file",
        str(input_file),
        "--output",
        str(output_path),
    ])

    assert exit_code == 0


def _sample_corpus_text() -> str:
    return "\n".join(
        [
            "From r Wed Jan 01 00:00:00 2001",
            _sample_message("First proposal", "https://example.net/reply"),
            "",
            "From r Thu Jan 02 00:00:00 2001",
            _sample_message("Second proposal", "https://example.org/reply"),
        ]
    )


def _sample_message(subject: str, url: str) -> str:
    return "\n".join(
        [
            "Return-Path: <sender@example.net>",
            "From: Sender <sender@example.net>",
            "Reply-To: Sender <reply@example.net>",
            "To: recipient@example.com",
            f"Subject: {subject}",
            "Content-Type: text/plain; charset=utf-8",
            "",
            f"Please reply at {url}.",
        ]
    )


def _latin1_sample_message_bytes() -> bytes:
    return b"\n".join(
        [
            b"Return-Path: <sender@example.net>",
            b"From: Sender <sender@example.net>",
            b"Subject: Oferta especial",
            b"Content-Type: text/plain; charset=iso-8859-1",
            b"",
            b"Transferencia especial para caf\xe9.",
        ]
    )
