import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence

from tools.ml_data_preparation.phishing_email_detection import (
    prepare_phishing_email_detection_row,
)
from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample


_EMAIL_TEXT_COLUMN = "Email Text"
_EMAIL_TYPE_COLUMN = "Email Type"
_URL_ONLY_PATTERN = re.compile(r"^https?://\S+$", re.IGNORECASE)
_ALPHA_PATTERN = re.compile(r"[a-zA-Z]")
_PHISHING_TERMS = (
    "login",
    "password",
    "verify",
    "account",
    "security",
    "invoice",
    "payment",
    "mfa",
    "2fa",
    "cloud",
    "document",
    "shared",
    "urgent",
    "suspended",
    "locked",
    "update",
    "confirm",
    "credentials",
    "reset",
    "sign in",
    "secure",
    "unusual activity",
)
_SPAM_TERMS = (
    "viagra",
    "adult",
    "porn",
    "mortgage",
    "loan",
    "lottery",
    "investment",
    "stock",
    "newsletter",
    "free gift",
    "sex",
    "casino",
    "pharmacy",
    "refinance",
    "winner",
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare the Phishing Email Detection CSV into JSONL samples.",
    )
    parser.add_argument("--input-file", required=True, help="Path to Phishing_Email.csv.")
    parser.add_argument("--output", required=True, help="Output JSONL path. Keep this outside the repository.")
    parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of rows to process.")

    args = parser.parse_args(argv)
    summary = prepare_phishing_email_detection_csv(
        input_file=Path(args.input_file),
        output_path=Path(args.output),
        limit=args.limit,
    )
    print_preparation_summary(summary)

    return 0 if summary.unsupported_label == 0 and summary.failed == 0 else 1


class PreparationSummary:
    def __init__(self) -> None:
        self.rows_read = 0
        self.processed = 0
        self.failed = 0
        self.skipped_empty_text = 0
        self.unsupported_label = 0
        self.duplicate_text = 0
        self.short_rows_lt_30 = 0
        self.long_rows_gt_10000 = 0
        self.url_only_rows = 0
        self.no_alpha_rows = 0
        self.urls_found = 0
        self.labels: Counter[str] = Counter()
        self.phishing_keyword_hits: Counter[str] = Counter()
        self.spam_keyword_hits: Counter[str] = Counter()


def prepare_phishing_email_detection_csv(
    input_file: Path,
    output_path: Path,
    limit: int | None = None,
) -> PreparationSummary:
    if limit is not None and limit < 0:
        raise ValueError("limit must be greater than or equal to zero")

    if not input_file.is_file():
        raise ValueError(f"input file does not exist: {input_file}")

    csv.field_size_limit(sys.maxsize)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = PreparationSummary()
    seen_texts: set[str] = set()

    with input_file.open("r", encoding="utf-8", errors="replace", newline="") as input_stream:
        reader = csv.DictReader(input_stream)
        _validate_columns(reader.fieldnames)

        with output_path.open("w", encoding="utf-8") as output_file:
            for csv_row_number, row in enumerate(reader, start=2):
                if limit is not None and summary.processed >= limit:
                    break

                summary.rows_read += 1
                email_text = str(row.get(_EMAIL_TEXT_COLUMN) or "")
                original_label = str(row.get(_EMAIL_TYPE_COLUMN) or "")
                stripped_text = email_text.strip()

                if stripped_text == "":
                    summary.skipped_empty_text += 1
                    continue

                _record_quality_counters(stripped_text, summary, seen_texts)
                source_id = _source_id_from_row(row=row, csv_row_number=csv_row_number)

                try:
                    sample = prepare_phishing_email_detection_row(
                        email_text=stripped_text,
                        source_id=source_id,
                        original_label=original_label,
                        csv_row_number=csv_row_number,
                    )
                except ValueError:
                    summary.unsupported_label += 1
                    continue
                except Exception as exc:
                    summary.failed += 1
                    print(f"FAILED row-{csv_row_number}: {exc}")
                    continue

                summary.processed += 1
                summary.labels[sample.normalized_label] += 1
                summary.urls_found += len(sample.urls)
                output_file.write(json.dumps(_sample_to_json_dict(sample), ensure_ascii=True, sort_keys=True))
                output_file.write("\n")

    return summary


def print_preparation_summary(summary: PreparationSummary) -> None:
    print(f"rows_read: {summary.rows_read}")
    print(f"processed: {summary.processed}")
    print(f"failed: {summary.failed}")
    print(f"skipped_empty_text: {summary.skipped_empty_text}")
    print(f"unsupported_label: {summary.unsupported_label}")
    print(f"duplicate_text: {summary.duplicate_text}")
    print(f"short_rows_lt_30: {summary.short_rows_lt_30}")
    print(f"long_rows_gt_10000: {summary.long_rows_gt_10000}")
    print(f"url_only_rows: {summary.url_only_rows}")
    print(f"no_alpha_rows: {summary.no_alpha_rows}")
    print(f"urls_found: {summary.urls_found}")
    print("labels:")
    for label, count in sorted(summary.labels.items()):
        print(f"  {label}: {count}")
    print("phishing_keyword_hits:")
    for term, count in sorted(summary.phishing_keyword_hits.items()):
        print(f"  {term}: {count}")
    print("spam_keyword_hits:")
    for term, count in sorted(summary.spam_keyword_hits.items()):
        print(f"  {term}: {count}")


def _validate_columns(columns: Sequence[str] | None) -> None:
    if columns is None:
        raise ValueError("input CSV has no header row")

    missing_columns = sorted({_EMAIL_TEXT_COLUMN, _EMAIL_TYPE_COLUMN}.difference(columns))
    if missing_columns:
        raise ValueError(f"input CSV is missing required columns: {', '.join(missing_columns)}")


def _source_id_from_row(row: dict[str, str], csv_row_number: int) -> str:
    row_id = str(row.get("") or "").strip()
    if row_id:
        return f"csv-{row_id}"

    return f"row-{csv_row_number}"


def _record_quality_counters(text: str, summary: PreparationSummary, seen_texts: set[str]) -> None:
    if text in seen_texts:
        summary.duplicate_text += 1
    else:
        seen_texts.add(text)

    lowered_text = text.lower()
    summary.short_rows_lt_30 += int(0 < len(text) < 30)
    summary.long_rows_gt_10000 += int(len(text) > 10_000)
    summary.url_only_rows += int(bool(_URL_ONLY_PATTERN.match(text)))
    summary.no_alpha_rows += int(not bool(_ALPHA_PATTERN.search(text)))

    for term in _PHISHING_TERMS:
        if term in lowered_text:
            summary.phishing_keyword_hits[term] += 1

    for term in _SPAM_TERMS:
        if term in lowered_text:
            summary.spam_keyword_hits[term] += 1


def _sample_to_json_dict(sample: PreparedEmailSample) -> dict[str, object]:
    return {
        "sample_id": sample.sample_id,
        "source": sample.source,
        "source_id": sample.source_id,
        "source_uri": sample.source_uri,
        "original_label": sample.original_label,
        "normalized_label": sample.normalized_label,
        "subject": sample.subject,
        "body_text": sample.body_text,
        "sender_domain": sample.sender_domain,
        "urls": list(sample.urls),
        "attachment_filenames": list(sample.attachment_filenames),
        "raw_available": sample.raw_available,
        "metadata": dict(sample.metadata),
    }


if __name__ == "__main__":
    raise SystemExit(main())
