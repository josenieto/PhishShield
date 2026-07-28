import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Sequence

from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample
from tools.ml_data_preparation.synthetic_suspicious_notifications import (
    iter_synthetic_suspicious_notification_templates,
    prepare_synthetic_suspicious_notification_template,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare synthetic suspicious notification templates into JSONL samples.")
    parser.add_argument("--output", required=True, help="Output JSONL path. Keep generated datasets outside Git.")
    parser.add_argument("--samples-per-category", type=int, default=10)
    args = parser.parse_args(argv)
    summary = prepare_synthetic_suspicious_notifications(Path(args.output), args.samples_per_category)
    print_preparation_summary(summary)
    return 0


class PreparationSummary:
    def __init__(self) -> None:
        self.processed = 0
        self.urls_found = 0
        self.categories: Counter[str] = Counter()
        self.sender_domains: Counter[str] = Counter()


def prepare_synthetic_suspicious_notifications(output_path: Path, samples_per_category: int = 10) -> PreparationSummary:
    if samples_per_category < 0:
        raise ValueError("samples_per_category must be greater than or equal to zero")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = PreparationSummary()
    templates = iter_synthetic_suspicious_notification_templates(samples_per_category=samples_per_category)
    with output_path.open("w", encoding="utf-8") as output_file:
        for template in templates:
            sample = prepare_synthetic_suspicious_notification_template(template)
            summary.processed += 1
            summary.urls_found += len(sample.urls)
            summary.categories[template.category] += 1
            summary.sender_domains[template.sender_domain] += 1
            output_file.write(json.dumps(_sample_to_json_dict(sample), ensure_ascii=True, sort_keys=True))
            output_file.write("\n")
    return summary


def print_preparation_summary(summary: PreparationSummary) -> None:
    print(f"processed: {summary.processed}")
    print(f"urls_found: {summary.urls_found}")
    print("categories:")
    for category, count in sorted(summary.categories.items()):
        print(f"  {category}: {count}")
    print("sender_domains:")
    for sender_domain, count in sorted(summary.sender_domains.items()):
        print(f"  {sender_domain}: {count}")


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
