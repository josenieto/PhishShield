import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Sequence


ALLOWED_NORMALIZED_LABELS = {
    "benign",
    "suspicious",
    "spam",
    "phishing",
    "fraud",
    "unknown",
}

REQUIRED_FIELDS = {
    "sample_id",
    "source",
    "source_id",
    "source_uri",
    "original_label",
    "normalized_label",
    "subject",
    "body_text",
    "sender_domain",
    "urls",
    "attachment_filenames",
    "raw_available",
    "metadata",
}


class ValidationSummary:
    def __init__(self) -> None:
        self.files = 0
        self.rows = 0
        self.invalid_rows = 0
        self.duplicate_sample_ids = 0
        self.empty_subject = 0
        self.empty_body = 0
        self.urls_found = 0
        self.labels: Counter[str] = Counter()
        self.errors: list[str] = []

    @property
    def is_valid(self) -> bool:
        return self.invalid_rows == 0 and self.duplicate_sample_ids == 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate prepared PhishShield ML JSONL datasets.",
    )
    parser.add_argument(
        "--input",
        action="append",
        required=True,
        help="Prepared JSONL file to validate. Can be provided multiple times.",
    )

    args = parser.parse_args(argv)
    summary = validate_prepared_datasets([Path(input_path) for input_path in args.input])
    print_validation_summary(summary)

    return 0 if summary.is_valid else 1


def validate_prepared_datasets(input_paths: Sequence[Path]) -> ValidationSummary:
    summary = ValidationSummary()
    seen_sample_ids: set[str] = set()

    for input_path in input_paths:
        summary.files += 1

        if not input_path.is_file():
            summary.invalid_rows += 1
            summary.errors.append(f"{input_path}: file does not exist")
            continue

        for line_number, line in enumerate(input_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue

            summary.rows += 1

            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                summary.invalid_rows += 1
                summary.errors.append(f"{input_path}:{line_number}: invalid JSON: {exc.msg}")
                continue

            if not isinstance(row, dict):
                summary.invalid_rows += 1
                summary.errors.append(f"{input_path}:{line_number}: row must be a JSON object")
                continue

            _validate_row(
                row=row,
                input_path=input_path,
                line_number=line_number,
                summary=summary,
                seen_sample_ids=seen_sample_ids,
            )

    return summary


def print_validation_summary(summary: ValidationSummary) -> None:
    print(f"files: {summary.files}")
    print(f"rows: {summary.rows}")
    print(f"invalid_rows: {summary.invalid_rows}")
    print(f"duplicate_sample_ids: {summary.duplicate_sample_ids}")
    print("labels:")
    for label, count in sorted(summary.labels.items()):
        print(f"  {label}: {count}")
    print(f"empty_subject: {summary.empty_subject}")
    print(f"empty_body: {summary.empty_body}")
    print(f"urls_found: {summary.urls_found}")

    if summary.errors:
        print("errors:")
        for error in summary.errors:
            print(f"  - {error}")


def _validate_row(
    row: dict[str, object],
    input_path: Path,
    line_number: int,
    summary: ValidationSummary,
    seen_sample_ids: set[str],
) -> None:
    row_is_valid = True
    missing_fields = sorted(REQUIRED_FIELDS.difference(row))

    if missing_fields:
        row_is_valid = False
        summary.errors.append(
            f"{input_path}:{line_number}: missing required fields: {', '.join(missing_fields)}"
        )

    sample_id = row.get("sample_id")
    if not isinstance(sample_id, str) or sample_id.strip() == "":
        row_is_valid = False
        summary.errors.append(f"{input_path}:{line_number}: sample_id must be a non-empty string")
    elif sample_id in seen_sample_ids:
        row_is_valid = False
        summary.duplicate_sample_ids += 1
        summary.errors.append(f"{input_path}:{line_number}: duplicate sample_id: {sample_id}")
    else:
        seen_sample_ids.add(sample_id)

    normalized_label = row.get("normalized_label")
    if not isinstance(normalized_label, str) or normalized_label not in ALLOWED_NORMALIZED_LABELS:
        row_is_valid = False
        summary.errors.append(f"{input_path}:{line_number}: invalid normalized_label: {normalized_label}")
    elif row_is_valid:
        summary.labels[normalized_label] += 1

    subject = row.get("subject")
    if isinstance(subject, str) and subject == "":
        summary.empty_subject += 1
    elif not isinstance(subject, str):
        row_is_valid = False
        summary.errors.append(f"{input_path}:{line_number}: subject must be a string")

    body_text = row.get("body_text")
    if isinstance(body_text, str) and body_text == "":
        summary.empty_body += 1
    elif not isinstance(body_text, str):
        row_is_valid = False
        summary.errors.append(f"{input_path}:{line_number}: body_text must be a string")

    urls = row.get("urls")
    if isinstance(urls, list):
        summary.urls_found += len(urls)
    else:
        row_is_valid = False
        summary.errors.append(f"{input_path}:{line_number}: urls must be a list")

    if not isinstance(row.get("attachment_filenames"), list):
        row_is_valid = False
        summary.errors.append(f"{input_path}:{line_number}: attachment_filenames must be a list")

    if not isinstance(row.get("metadata"), dict):
        row_is_valid = False
        summary.errors.append(f"{input_path}:{line_number}: metadata must be an object")

    if not row_is_valid:
        summary.invalid_rows += 1


if __name__ == "__main__":
    raise SystemExit(main())
