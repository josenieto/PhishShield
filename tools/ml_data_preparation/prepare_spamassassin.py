import argparse
import json
from pathlib import Path
from typing import Sequence

from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample
from tools.ml_data_preparation.spamassassin import prepare_spamassassin_email


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a local SpamAssassin email directory into JSONL samples.",
    )
    parser.add_argument("--input-dir", required=True, help="Directory containing raw SpamAssassin email files.")
    parser.add_argument("--label", required=True, help="SpamAssassin source label such as easy_ham, hard_ham, ham, or spam.")
    parser.add_argument("--output", required=True, help="Output JSONL path. Keep this outside the repository.")
    parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of files to process.")

    args = parser.parse_args(argv)

    summary = prepare_spamassassin_directory(
        input_dir=Path(args.input_dir),
        label=args.label,
        output_path=Path(args.output),
        limit=args.limit,
    )

    print(f"processed: {summary.processed}")
    print(f"failed: {summary.failed}")
    print(f"empty_subject: {summary.empty_subject}")
    print(f"empty_body: {summary.empty_body}")
    print(f"urls_found: {summary.urls_found}")

    return 0 if summary.failed == 0 else 1


class PreparationSummary:
    def __init__(self) -> None:
        self.processed = 0
        self.failed = 0
        self.empty_subject = 0
        self.empty_body = 0
        self.urls_found = 0


def prepare_spamassassin_directory(
    input_dir: Path,
    label: str,
    output_path: Path,
    limit: int | None = None,
) -> PreparationSummary:
    if limit is not None and limit < 0:
        raise ValueError("limit must be greater than or equal to zero")

    if not input_dir.is_dir():
        raise ValueError(f"input directory does not exist: {input_dir}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = PreparationSummary()
    processed_files = 0

    with output_path.open("w", encoding="utf-8") as output_file:
        for input_path in sorted(input_dir.iterdir()):
            if not input_path.is_file():
                continue

            if limit is not None and processed_files >= limit:
                break

            processed_files += 1

            try:
                sample = prepare_spamassassin_email(
                    raw_email=input_path.read_bytes(),
                    source_id=input_path.name,
                    original_label=label,
                )
            except Exception as exc:
                summary.failed += 1
                print(f"FAILED {input_path.name}: {exc}")
                continue

            summary.processed += 1
            summary.empty_subject += int(sample.subject == "")
            summary.empty_body += int(sample.body_text == "")
            summary.urls_found += len(sample.urls)
            output_file.write(json.dumps(_sample_to_json_dict(sample), ensure_ascii=False, sort_keys=True))
            output_file.write("\n")

    return summary


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
