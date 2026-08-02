"""Evaluate the baseline against an external JSONL text holdout."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)
from tools.ml_data_preparation.phishshield_fixtures import (
    NORMALIZED_LABEL_BENIGN,
    NORMALIZED_LABEL_SUSPICIOUS,
)
from tools.ml_training.evaluate_fixture_holdout import _predict_label, _train_model
from tools.ml_training.train_baseline import (
    FEATURE_SET_TEXT,
    FEATURE_SET_TEXT_WITH_LIGHT_METADATA,
)


@dataclass(frozen=True)
class ExternalPrediction:
    sample_id: str
    expected_label: str
    predicted_label: str
    intent: str
    technique: str
    target: str
    source: str
    suspicious_probability: float | None

    @property
    def is_correct(self) -> bool:
        return self.expected_label == self.predicted_label


@dataclass(frozen=True)
class ExternalHoldoutResult:
    predictions: tuple[ExternalPrediction, ...]

    @property
    def total(self) -> int:
        return len(self.predictions)

    @property
    def accuracy(self) -> float:
        if not self.predictions:
            return 0.0
        return sum(prediction.is_correct for prediction in self.predictions) / self.total

    @property
    def false_positive_benign(self) -> int:
        return sum(
            prediction.expected_label == NORMALIZED_LABEL_BENIGN
            and prediction.predicted_label == NORMALIZED_LABEL_SUSPICIOUS
            for prediction in self.predictions
        )

    @property
    def false_negative_suspicious(self) -> int:
        return sum(
            prediction.expected_label == NORMALIZED_LABEL_SUSPICIOUS
            and prediction.predicted_label == NORMALIZED_LABEL_BENIGN
            for prediction in self.predictions
        )

    def metrics_by(self, field: str) -> dict[str, dict[str, float | int]]:
        if field not in {"expected_label", "intent", "technique", "target", "source"}:
            raise ValueError(f"Unsupported metric dimension: {field}")

        groups: dict[str, list[ExternalPrediction]] = {}
        for prediction in self.predictions:
            value = str(getattr(prediction, field) or "unknown")
            groups.setdefault(value, []).append(prediction)

        result: dict[str, dict[str, float | int]] = {}
        for value, predictions in sorted(groups.items()):
            total = len(predictions)
            benign_total = sum(p.expected_label == NORMALIZED_LABEL_BENIGN for p in predictions)
            suspicious_total = sum(p.expected_label == NORMALIZED_LABEL_SUSPICIOUS for p in predictions)
            false_positive = sum(
                p.expected_label == NORMALIZED_LABEL_BENIGN
                and p.predicted_label == NORMALIZED_LABEL_SUSPICIOUS
                for p in predictions
            )
            false_negative = sum(
                p.expected_label == NORMALIZED_LABEL_SUSPICIOUS
                and p.predicted_label == NORMALIZED_LABEL_BENIGN
                for p in predictions
            )
            result[value] = {
                "total": total,
                "accuracy": sum(p.is_correct for p in predictions) / total,
                "benign_total": benign_total,
                "suspicious_total": suspicious_total,
                "false_positive_benign": false_positive,
                "false_negative_suspicious": false_negative,
            }
        return result


def evaluate_external_holdout(
    input_paths: Sequence[Path],
    holdout_path: Path,
    feature_set: str = FEATURE_SET_TEXT_WITH_LIGHT_METADATA,
    random_seed: int = 42,
    suspicious_threshold: float = 0.5,
) -> ExternalHoldoutResult:
    if feature_set not in {FEATURE_SET_TEXT, FEATURE_SET_TEXT_WITH_LIGHT_METADATA}:
        raise ValueError(f"Unsupported feature set: {feature_set}")
    if not 0.0 <= suspicious_threshold <= 1.0:
        raise ValueError("suspicious_threshold must be between 0.0 and 1.0")

    training_samples = _load_training_samples(input_paths)
    model = _train_model(_balanced_samples(training_samples, random_seed), feature_set)
    parser_adapter = PythonEmailContentExtractorAdapter()
    predictions: list[ExternalPrediction] = []

    for line_number, row in enumerate(_load_holdout_rows(holdout_path), start=1):
        expected_label = _normalize_label(row.get("label"))
        if expected_label is None:
            raise ValueError(f"unsupported label on holdout line {line_number}: {row.get('label')}")
        sample_id = str(row.get("id") or f"row-{line_number}")
        text = _row_to_text(row, feature_set, parser_adapter)
        predicted_label, probability = _predict_label(model, text, suspicious_threshold)
        predictions.append(
            ExternalPrediction(
                sample_id=sample_id,
                expected_label=expected_label,
                predicted_label=predicted_label,
                intent=str(row.get("intent") or "unknown"),
                technique=str(row.get("technique") or "unknown"),
                target=str(row.get("target") or "unknown"),
                source=str(row.get("source") or "external-holdout"),
                suspicious_probability=probability,
            )
        )

    return ExternalHoldoutResult(predictions=tuple(predictions))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate the baseline against an external JSONL email holdout.")
    parser.add_argument("--input", action="append", required=True, help="Prepared training JSONL file.")
    parser.add_argument("--holdout", required=True, help="External JSONL holdout file. Keep it outside Git.")
    parser.add_argument("--feature-set", default=FEATURE_SET_TEXT_WITH_LIGHT_METADATA, choices=[FEATURE_SET_TEXT, FEATURE_SET_TEXT_WITH_LIGHT_METADATA])
    parser.add_argument("--random-seed", type=int, default=42)
    parser.add_argument("--suspicious-threshold", type=float, default=0.5)
    args = parser.parse_args(argv)

    result = evaluate_external_holdout(
        input_paths=[Path(path) for path in args.input],
        holdout_path=Path(args.holdout),
        feature_set=args.feature_set,
        random_seed=args.random_seed,
        suspicious_threshold=args.suspicious_threshold,
    )
    print_external_result(result)
    return 0


def print_external_result(result: ExternalHoldoutResult) -> None:
    print(f"total: {result.total}")
    print(f"accuracy: {result.accuracy:.4f}")
    print(f"false_positive_benign: {result.false_positive_benign}")
    print(f"false_negative_suspicious: {result.false_negative_suspicious}")
    for dimension in ("expected_label", "intent", "technique", "target"):
        print(f"metrics_by_{dimension}:")
        for value, metrics in result.metrics_by(dimension).items():
            print(f"  {value}: {json.dumps(metrics, sort_keys=True)}")


def _load_training_samples(input_paths: Sequence[Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in input_paths:
        rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return rows


def _balanced_samples(samples: list[dict[str, object]], random_seed: int) -> list[dict[str, object]]:
    from tools.ml_training.evaluate_fixture_holdout import _balanced_samples as balance

    return balance(samples, random_seed)


def _load_holdout_rows(path: Path) -> list[dict[str, object]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError("external holdout must contain at least one row")
    return rows


def _normalize_label(value: object) -> str | None:
    normalized = str(value or "").strip().lower()
    if normalized == "benign":
        return NORMALIZED_LABEL_BENIGN
    if normalized in {"phishing", "suspicious"}:
        return NORMALIZED_LABEL_SUSPICIOUS
    return None


def _row_to_text(
    row: dict[str, object],
    feature_set: str,
    parser_adapter: PythonEmailContentExtractorAdapter | None = None,
) -> str:
    # Reuse the runtime parser so external body URLs are represented consistently.
    parser = parser_adapter or PythonEmailContentExtractorAdapter()
    raw_email = "\r\n".join(
        (
            "From: External Holdout <holdout@example.test>",
            f"Subject: {str(row.get('subject') or '')}",
            "Content-Type: text/plain; charset=utf-8",
            "",
            str(row.get("body") or ""),
        )
    ).encode("utf-8")
    extracted = parser.extract(raw_email)
    text_parts = [extracted.subject, extracted.body_text]
    if feature_set == FEATURE_SET_TEXT_WITH_LIGHT_METADATA:
        text_parts.extend(extracted.urls)
        text_parts.extend(extracted.attachment_filenames)
    return "\n".join(text_parts)


if __name__ == "__main__":
    raise SystemExit(main())
