import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Sequence

from tools.ml_data_preparation.enron import enron_source_id_from_path, prepare_enron_email
from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a capped Enron maildir sample into JSONL samples.",
    )
    parser.add_argument("--input-dir", required=True, help="Path to the extracted Enron maildir directory.")
    parser.add_argument("--output", required=True, help="Output JSONL path. Keep this outside the repository.")
    parser.add_argument("--limit", type=int, default=1_000, help="Maximum number of prepared messages to write.")
    parser.add_argument("--max-per-user", type=int, default=None, help="Optional maximum prepared messages per mailbox user.")
    parser.add_argument("--max-per-folder", type=int, default=None, help="Optional maximum prepared messages per folder path.")

    args = parser.parse_args(argv)
    summary = prepare_enron_directory(
        input_dir=Path(args.input_dir),
        output_path=Path(args.output),
        limit=args.limit,
        max_per_user=args.max_per_user,
        max_per_folder=args.max_per_folder,
    )
    print_preparation_summary(summary)

    return 0 if summary.failed == 0 else 1


class PreparationSummary:
    def __init__(self) -> None:
        self.discovered_files = 0
        self.processed = 0
        self.failed = 0
        self.skipped_empty_body = 0
        self.skipped_user_limit = 0
        self.skipped_folder_limit = 0
        self.duplicate_body = 0
        self.duplicate_subject_body = 0
        self.empty_subject = 0
        self.short_rows_lt_30 = 0
        self.long_rows_gt_10000 = 0
        self.urls_found = 0
        self.users: Counter[str] = Counter()
        self.folders: Counter[str] = Counter()
        self.sender_domains: Counter[str] = Counter()


def prepare_enron_directory(
    input_dir: Path,
    output_path: Path,
    limit: int | None = 1_000,
    max_per_user: int | None = None,
    max_per_folder: int | None = None,
) -> PreparationSummary:
    if limit is not None and limit < 0:
        raise ValueError("limit must be greater than or equal to zero")

    if max_per_user is not None and max_per_user < 0:
        raise ValueError("max_per_user must be greater than or equal to zero")

    if max_per_folder is not None and max_per_folder < 0:
        raise ValueError("max_per_folder must be greater than or equal to zero")

    if not input_dir.is_dir():
        raise ValueError(f"input directory does not exist: {input_dir}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = PreparationSummary()
    seen_body_texts: set[str] = set()
    seen_subject_body_texts: set[str] = set()

    with output_path.open("w", encoding="utf-8") as output_file:
        for email_path in _iter_email_paths(input_dir):
            if limit is not None and summary.processed >= limit:
                break

            summary.discovered_files += 1
            source_id = enron_source_id_from_path(input_dir=input_dir, email_path=email_path)
            mailbox_user, folder = _parse_source_id(source_id)

            if max_per_user is not None and summary.users[mailbox_user] >= max_per_user:
                summary.skipped_user_limit += 1
                continue

            if max_per_folder is not None and summary.folders[folder] >= max_per_folder:
                summary.skipped_folder_limit += 1
                continue

            try:
                sample = prepare_enron_email(
                    raw_email=_read_email_bytes(email_path),
                    source_id=source_id,
                    relative_path=source_id,
                )
            except Exception as exc:
                summary.failed += 1
                print(f"FAILED {source_id}: {exc}")
                continue

            if sample.body_text == "":
                summary.skipped_empty_body += 1
                continue

            _record_quality_counters(
                sample=sample,
                summary=summary,
                seen_body_texts=seen_body_texts,
                seen_subject_body_texts=seen_subject_body_texts,
            )
            summary.processed += 1
            output_file.write(json.dumps(_sample_to_json_dict(sample), ensure_ascii=True, sort_keys=True))
            output_file.write("\n")

    return summary


def _iter_email_paths(input_dir: Path):
    for root, dirnames, filenames in os.walk(input_dir):
        dirnames.sort()
        for filename in sorted(filenames):
            yield Path(root) / filename


def _read_email_bytes(email_path: Path) -> bytes:
    if os.name != "nt":
        return email_path.read_bytes()

    # Enron files commonly end with a trailing dot, which requires the Windows
    # extended path prefix to open reliably.
    absolute_path = str(email_path.resolve())
    extended_path = absolute_path if absolute_path.startswith("\\\\?\\") else f"\\\\?\\{absolute_path}"
    with open(extended_path, "rb") as email_file:
        return email_file.read()


def print_preparation_summary(summary: PreparationSummary) -> None:
    print(f"discovered_files: {summary.discovered_files}")
    print(f"processed: {summary.processed}")
    print(f"failed: {summary.failed}")
    print(f"skipped_empty_body: {summary.skipped_empty_body}")
    print(f"skipped_user_limit: {summary.skipped_user_limit}")
    print(f"skipped_folder_limit: {summary.skipped_folder_limit}")
    print(f"duplicate_body: {summary.duplicate_body}")
    print(f"duplicate_subject_body: {summary.duplicate_subject_body}")
    print(f"empty_subject: {summary.empty_subject}")
    print(f"short_rows_lt_30: {summary.short_rows_lt_30}")
    print(f"long_rows_gt_10000: {summary.long_rows_gt_10000}")
    print(f"urls_found: {summary.urls_found}")
    print(f"users_seen: {len(summary.users)}")
    print(f"folders_seen: {len(summary.folders)}")
    print("top_users:")
    for user, count in summary.users.most_common(10):
        print(f"  {user}: {count}")
    print("top_folders:")
    for folder, count in summary.folders.most_common(10):
        print(f"  {folder}: {count}")
    print("top_sender_domains:")
    for sender_domain, count in summary.sender_domains.most_common(10):
        print(f"  {sender_domain}: {count}")


def _parse_source_id(source_id: str) -> tuple[str, str]:
    parts = source_id.replace("\\", "/").split("/")
    if len(parts) < 3:
        return "", ""

    return parts[0], "/".join(parts[1:-1])


def _record_quality_counters(
    sample: PreparedEmailSample,
    summary: PreparationSummary,
    seen_body_texts: set[str],
    seen_subject_body_texts: set[str],
) -> None:
    summary.empty_subject += int(sample.subject == "")
    summary.short_rows_lt_30 += int(0 < len(sample.body_text) < 30)
    summary.long_rows_gt_10000 += int(len(sample.body_text) > 10_000)
    summary.urls_found += len(sample.urls)
    summary.users[str(sample.metadata.get("mailbox_user", ""))] += 1
    summary.folders[str(sample.metadata.get("folder", ""))] += 1

    if sample.sender_domain:
        summary.sender_domains[sample.sender_domain] += 1

    if sample.body_text in seen_body_texts:
        summary.duplicate_body += 1
    else:
        seen_body_texts.add(sample.body_text)

    subject_body = "\n".join((sample.subject, sample.body_text))
    if subject_body in seen_subject_body_texts:
        summary.duplicate_subject_body += 1
    else:
        seen_subject_body_texts.add(subject_body)


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
