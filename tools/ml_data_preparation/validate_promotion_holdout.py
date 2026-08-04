"""Validate the manifest for the independent promotion holdout."""

import argparse
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Sequence


PROMOTION_FAMILIES = (
    "account",
    "mfa_security",
    "cloud_document_sharing",
    "billing_invoices",
    "support",
    "hr",
    "vendor_portals",
    "newsletter_preferences",
)
EXPECTED_PER_GROUP = 20
EXPECTED_TOTAL = len(PROMOTION_FAMILIES) * EXPECTED_PER_GROUP * 2
ALLOWED_LABELS = {"benign", "suspicious"}
REQUIRED_FIELDS = {
    "sample_id",
    "expected_label",
    "family",
    "source",
    "source_uri",
    "license",
    "collection_date",
    "language",
    "content_hash",
    "raw_available",
    "review_status",
}
APPROVED_STATUS = "approved"
SHA256_LENGTH = hashlib.sha256().digest_size * 2


class PromotionHoldoutValidation:
    def __init__(self) -> None:
        self.rows = 0
        self.invalid_rows = 0
        self.duplicate_sample_ids = 0
        self.duplicate_content_hashes = 0
        self.errors: list[str] = []
        self.counts: Counter[tuple[str, str]] = Counter()

    @property
    def is_valid(self) -> bool:
        return self.invalid_rows == 0 and self.rows == EXPECTED_TOTAL and all(
            self.counts[(family, label)] == EXPECTED_PER_GROUP
            for family in PROMOTION_FAMILIES
            for label in sorted(ALLOWED_LABELS)
        )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a PhishShield promotion holdout manifest.")
    parser.add_argument("--input", required=True, help="Promotion holdout manifest JSONL path.")
    args = parser.parse_args(argv)

    result = validate_promotion_holdout(Path(args.input))
    print_validation(result)
    return 0 if result.is_valid else 1


def validate_promotion_holdout(path: Path) -> PromotionHoldoutValidation:
    result = PromotionHoldoutValidation()
    seen_sample_ids: set[str] = set()
    seen_hashes: set[str] = set()

    if not path.is_file():
        result.invalid_rows = 1
        result.errors.append(f"{path}: file does not exist")
        return result

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        result.rows += 1
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            result.invalid_rows += 1
            result.errors.append(f"{path}:{line_number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(row, dict):
            result.invalid_rows += 1
            result.errors.append(f"{path}:{line_number}: row must be an object")
            continue
        _validate_row(row, path, line_number, result, seen_sample_ids, seen_hashes)

    if result.rows != EXPECTED_TOTAL:
        result.errors.append(f"expected {EXPECTED_TOTAL} rows, found {result.rows}")
    for family in PROMOTION_FAMILIES:
        for label in sorted(ALLOWED_LABELS):
            count = result.counts[(family, label)]
            if count != EXPECTED_PER_GROUP:
                result.errors.append(f"{family}/{label}: expected {EXPECTED_PER_GROUP} rows, found {count}")
    return result


def print_validation(result: PromotionHoldoutValidation) -> None:
    print(f"rows: {result.rows}")
    print(f"invalid_rows: {result.invalid_rows}")
    print(f"duplicate_sample_ids: {result.duplicate_sample_ids}")
    print(f"duplicate_content_hashes: {result.duplicate_content_hashes}")
    print("counts:")
    for (family, label), count in sorted(result.counts.items()):
        print(f"  {family}/{label}: {count}")
    if result.errors:
        print("errors:")
        for error in result.errors:
            print(f"  - {error}")


def _validate_row(
    row: dict[str, object],
    path: Path,
    line_number: int,
    result: PromotionHoldoutValidation,
    seen_sample_ids: set[str],
    seen_hashes: set[str],
) -> None:
    valid = True
    missing = sorted(REQUIRED_FIELDS.difference(row))
    if missing:
        valid = False
        result.errors.append(f"{path}:{line_number}: missing required fields: {', '.join(missing)}")

    sample_id = row.get("sample_id")
    if not isinstance(sample_id, str) or not sample_id.strip():
        valid = False
        result.errors.append(f"{path}:{line_number}: sample_id must be a non-empty string")
    elif sample_id in seen_sample_ids:
        valid = False
        result.duplicate_sample_ids += 1
        result.errors.append(f"{path}:{line_number}: duplicate sample_id: {sample_id}")
    else:
        seen_sample_ids.add(sample_id)

    label = row.get("expected_label")
    family = row.get("family")
    if label not in ALLOWED_LABELS:
        valid = False
        result.errors.append(f"{path}:{line_number}: invalid expected_label: {label}")
    if family not in PROMOTION_FAMILIES:
        valid = False
        result.errors.append(f"{path}:{line_number}: invalid family: {family}")

    for field in ("source", "source_uri", "license", "language", "review_status"):
        if not isinstance(row.get(field), str) or not str(row[field]).strip():
            valid = False
            result.errors.append(f"{path}:{line_number}: {field} must be a non-empty string")
    if row.get("language") != "en":
        valid = False
        result.errors.append(f"{path}:{line_number}: language must be 'en'")
    if row.get("review_status") != APPROVED_STATUS:
        valid = False
        result.errors.append(f"{path}:{line_number}: review_status must be '{APPROVED_STATUS}'")

    collection_date = row.get("collection_date")
    try:
        date.fromisoformat(str(collection_date))
    except ValueError:
        valid = False
        result.errors.append(f"{path}:{line_number}: collection_date must be ISO-8601 date")

    content_hash = row.get("content_hash")
    if not isinstance(content_hash, str) or len(content_hash) != SHA256_LENGTH:
        valid = False
        result.errors.append(f"{path}:{line_number}: content_hash must be a SHA-256 hex digest")
    else:
        try:
            int(content_hash, 16)
        except ValueError:
            valid = False
            result.errors.append(f"{path}:{line_number}: content_hash must be hexadecimal")
        if content_hash in seen_hashes:
            valid = False
            result.duplicate_content_hashes += 1
            result.errors.append(f"{path}:{line_number}: duplicate content_hash: {content_hash}")
        else:
            seen_hashes.add(content_hash)

    if not isinstance(row.get("raw_available"), bool):
        valid = False
        result.errors.append(f"{path}:{line_number}: raw_available must be boolean")

    if valid and isinstance(family, str) and isinstance(label, str):
        result.counts[(family, label)] += 1
    else:
        result.invalid_rows += 1


if __name__ == "__main__":
    raise SystemExit(main())
