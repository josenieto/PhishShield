import argparse
import json
from pathlib import Path
from typing import Sequence

from tools.ml_data_preparation.fraudulent_email_corpus import (
    prepare_fraudulent_email_corpus_message,
    split_fraudulent_email_corpus_message_bytes,
)
from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare the Fraudulent E-mail Corpus text file into JSONL samples.",
    )
    parser.add_argument("--input-file", required=True, help="Path to the corpus text file.")
    parser.add_argument("--output", required=True, help="Output JSONL path. Keep this outside the repository.")
    parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of messages to process.")

    args = parser.parse_args(argv)

    summary = prepare_fraudulent_email_corpus_file(
        input_file=Path(args.input_file),
        output_path=Path(args.output),
        limit=args.limit,
    )

    print(f"discovered: {summary.discovered}")
    print(f"processed: {summary.processed}")
    print(f"failed: {summary.failed}")
    print(f"empty_subject: {summary.empty_subject}")
    print(f"empty_body: {summary.empty_body}")
    print(f"urls_found: {summary.urls_found}")

    return 0 if summary.failed == 0 else 1


class PreparationSummary:
    def __init__(self) -> None:
        self.discovered = 0
        self.processed = 0
        self.failed = 0
        self.empty_subject = 0
        self.empty_body = 0
        self.urls_found = 0


def prepare_fraudulent_email_corpus_file(
    input_file: Path,
    output_path: Path,
    limit: int | None = None,
) -> PreparationSummary:
    if limit is not None and limit < 0:
        raise ValueError("limit must be greater than or equal to zero")

    if not input_file.is_file():
        raise ValueError(f"input file does not exist: {input_file}")

    corpus_bytes = input_file.read_bytes()
    messages = split_fraudulent_email_corpus_message_bytes(corpus_bytes)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = PreparationSummary()
    summary.discovered = len(messages)

    with output_path.open("w", encoding="utf-8") as output_file:
        for index, message in enumerate(messages, start=1):
            if limit is not None and summary.processed >= limit:
                break

            source_id = f"message-{index:05d}"
            try:
                sample = prepare_fraudulent_email_corpus_message(
                    raw_message=message,
                    source_id=source_id,
                )
            except Exception as exc:
                summary.failed += 1
                print(f"FAILED {source_id}: {exc}")
                continue

            summary.processed += 1
            summary.empty_subject += int(sample.subject == "")
            summary.empty_body += int(sample.body_text == "")
            summary.urls_found += len(sample.urls)
            output_file.write(json.dumps(_sample_to_json_dict(sample), ensure_ascii=True, sort_keys=True))
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
