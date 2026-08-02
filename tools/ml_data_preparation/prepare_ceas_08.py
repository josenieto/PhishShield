import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence

from tools.ml_data_preparation.ceas_08 import prepare_ceas_08_row
from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample


REQUIRED_COLUMNS = {"sender", "receiver", "date", "subject", "body", "label", "urls"}


class PreparationSummary:
    def __init__(self) -> None:
        self.rows_read = 0
        self.processed = 0
        self.failed = 0
        self.unsupported_label = 0
        self.empty_subject = 0
        self.empty_body = 0
        self.duplicate_content = 0
        self.urls_found = 0
        self.labels: Counter[str] = Counter()


def prepare_ceas_08_csv(
    input_file: Path,
    output_path: Path,
    label_map: dict[str, str],
    limit: int | None = None,
) -> PreparationSummary:
    if limit is not None and limit < 0:
        raise ValueError("limit must be greater than or equal to zero")
    if not input_file.is_file():
        raise ValueError(f"input file does not exist: {input_file}")

    csv.field_size_limit(sys.maxsize)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = PreparationSummary()
    seen_content: set[tuple[str, str]] = set()

    with input_file.open("r", encoding="utf-8", errors="replace", newline="") as source:
        reader = csv.DictReader(source)
        _validate_columns(reader.fieldnames)
        with output_path.open("w", encoding="utf-8") as target:
            for row_number, row in enumerate(reader, start=2):
                if limit is not None and summary.rows_read >= limit:
                    break
                summary.rows_read += 1
                subject = str(row.get("subject") or "").strip()
                body = str(row.get("body") or "").strip()
                summary.empty_subject += not subject
                summary.empty_body += not body
                if (subject, body) in seen_content:
                    summary.duplicate_content += 1
                seen_content.add((subject, body))

                try:
                    sample = prepare_ceas_08_row(row, row_number, label_map)
                except ValueError:
                    summary.unsupported_label += 1
                    continue
                except Exception:
                    summary.failed += 1
                    continue

                summary.processed += 1
                summary.labels[sample.normalized_label] += 1
                summary.urls_found += len(sample.urls)
                target.write(json.dumps(_to_dict(sample), ensure_ascii=True, sort_keys=True) + "\n")

    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare CEAS-08 CSV for external evaluation.")
    parser.add_argument("--input-file", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--label-map", action="append", required=True, help="Mapping such as 0=benign or 1=suspicious.")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)
    label_map = _parse_label_maps(args.label_map)
    summary = prepare_ceas_08_csv(Path(args.input_file), Path(args.output), label_map, args.limit)
    for key, value in vars(summary).items():
        print(f"{key}: {dict(value) if isinstance(value, Counter) else value}")
    return 0 if summary.failed == 0 and summary.unsupported_label == 0 else 1


def _parse_label_maps(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"invalid label map: {value}")
        source, normalized = value.split("=", maxsplit=1)
        result[source.strip()] = normalized.strip()
    return result


def _validate_columns(columns: Sequence[str] | None) -> None:
    if columns is None or not REQUIRED_COLUMNS.issubset(columns):
        missing = sorted(REQUIRED_COLUMNS.difference(columns or []))
        raise ValueError(f"input CSV is missing required columns: {', '.join(missing)}")


def _to_dict(sample: PreparedEmailSample) -> dict[str, object]:
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
