import json
import hashlib
from pathlib import Path

from tools.ml_data_preparation.validate_promotion_holdout import (
    EXPECTED_TOTAL,
    PROMOTION_FAMILIES,
    validate_promotion_holdout,
)


def test_should_accept_complete_balanced_promotion_manifest(tmp_path: Path) -> None:
    manifest = tmp_path / "promotion.jsonl"
    rows = [
        _row(f"{family}-{label}-{index}", family, label, index)
        for family in PROMOTION_FAMILIES
        for label in ("benign", "suspicious")
        for index in range(20)
    ]
    manifest.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    result = validate_promotion_holdout(manifest)

    assert result.is_valid
    assert result.rows == EXPECTED_TOTAL
    assert result.invalid_rows == 0


def test_should_reject_unbalanced_or_duplicate_promotion_manifest(tmp_path: Path) -> None:
    manifest = tmp_path / "promotion.jsonl"
    rows = [_row("duplicate", PROMOTION_FAMILIES[0], "benign", 0)]
    rows.append(_row("duplicate", PROMOTION_FAMILIES[0], "benign", 0))
    manifest.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    result = validate_promotion_holdout(manifest)

    assert not result.is_valid
    assert result.duplicate_sample_ids == 1
    assert any("expected 320 rows" in error for error in result.errors)


def _row(sample_id: str, family: str, label: str, index: int) -> dict[str, object]:
    return {
        "sample_id": sample_id,
        "expected_label": label,
        "family": family,
        "source": "public-source",
        "source_uri": "https://example.test/source",
        "license": "reviewed-source-terms",
        "collection_date": "2026-07-28",
        "language": "en",
        "content_hash": hashlib.sha256(sample_id.encode("utf-8")).hexdigest(),
        "raw_available": False,
        "review_status": "approved",
    }
