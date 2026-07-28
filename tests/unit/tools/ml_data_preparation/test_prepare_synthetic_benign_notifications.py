import json
from pathlib import Path

import pytest

from tools.ml_data_preparation.prepare_synthetic_benign_notifications import (
    main,
    prepare_synthetic_benign_notifications,
)


def test_should_prepare_synthetic_benign_notifications_to_jsonl(tmp_path: Path) -> None:
    output_path = tmp_path / "prepared" / "synthetic_benign_notifications.jsonl"

    summary = prepare_synthetic_benign_notifications(
        output_path=output_path,
        samples_per_category=2,
    )
    rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

    assert summary.processed == 24
    assert summary.urls_found == 24
    assert len(summary.categories) == 12
    assert all(count == 2 for count in summary.categories.values())
    assert len(rows) == 24
    assert rows[0]["source"] == "synthetic_benign_notifications"
    assert rows[0]["original_label"] == "synthetic_benign"
    assert rows[0]["normalized_label"] == "benign"
    assert rows[0]["raw_available"] is False
    assert rows[0]["metadata"]["category"] == "account_activity_summary"


def test_should_reject_negative_samples_per_category(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="samples_per_category must be greater than or equal to zero"):
        prepare_synthetic_benign_notifications(
            output_path=tmp_path / "output.jsonl",
            samples_per_category=-1,
        )


def test_should_return_zero_from_cli(tmp_path: Path) -> None:
    output_path = tmp_path / "prepared" / "synthetic_benign_notifications.jsonl"

    exit_code = main([
        "--output",
        str(output_path),
        "--samples-per-category",
        "1",
    ])

    assert exit_code == 0
    assert len(output_path.read_text(encoding="utf-8").splitlines()) == 12
