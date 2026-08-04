"""Evaluate the current baseline against prepared JSONL holdout data."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from tools.ml_data_preparation.phishshield_fixtures import (
    NORMALIZED_LABEL_BENIGN,
    NORMALIZED_LABEL_SUSPICIOUS,
)
from tools.ml_training.evaluate_fixture_holdout import _balanced_samples, _predict_label, _train_model
from tools.ml_training.train_baseline import FEATURE_SET_TEXT, FEATURE_SET_TEXT_WITH_LIGHT_METADATA
from tools.ml_training.confidence_policy import classify_suspicious_probability


@dataclass(frozen=True)
class PreparedHoldoutPrediction:
    sample_id: str
    expected_label: str
    predicted_label: str
    source: str
    source_url_flag: str
    body_length_bucket: str
    url_count: int
    suspicious_probability: float | None
    family: str = "unclassified"

    @property
    def is_correct(self) -> bool:
        return self.expected_label == self.predicted_label


@dataclass(frozen=True)
class PreparedHoldoutResult:
    predictions: tuple[PreparedHoldoutPrediction, ...]

    @property
    def total(self) -> int:
        return len(self.predictions)

    @property
    def accuracy(self) -> float:
        return sum(p.is_correct for p in self.predictions) / self.total if self.total else 0.0

    @property
    def false_positive_benign(self) -> int:
        return sum(p.expected_label == NORMALIZED_LABEL_BENIGN and p.predicted_label == NORMALIZED_LABEL_SUSPICIOUS for p in self.predictions)

    @property
    def false_negative_suspicious(self) -> int:
        return sum(p.expected_label == NORMALIZED_LABEL_SUSPICIOUS and p.predicted_label == NORMALIZED_LABEL_BENIGN for p in self.predictions)

    @property
    def inconclusive(self) -> int:
        return sum(p.predicted_label == "inconclusive" for p in self.predictions)

    @property
    def coverage(self) -> float:
        return 0.0 if not self.predictions else (self.total - self.inconclusive) / self.total

    @property
    def abstention_rate(self) -> float:
        return 0.0 if not self.predictions else self.inconclusive / self.total

    @property
    def conditional_accuracy(self) -> float:
        classified = [p for p in self.predictions if p.predicted_label != "inconclusive"]
        return 0.0 if not classified else sum(p.is_correct for p in classified) / len(classified)

    @property
    def confident_false_positive_rate(self) -> float:
        benign = [p for p in self.predictions if p.expected_label == NORMALIZED_LABEL_BENIGN]
        return 0.0 if not benign else self.false_positive_benign / len(benign)

    @property
    def confident_false_negative_rate(self) -> float:
        suspicious = [p for p in self.predictions if p.expected_label == NORMALIZED_LABEL_SUSPICIOUS]
        return 0.0 if not suspicious else self.false_negative_suspicious / len(suspicious)

    def metrics_by(self, dimension: str) -> dict[str, dict[str, float | int]]:
        allowed = {"expected_label", "family", "source_url_flag", "body_length_bucket"}
        if dimension not in allowed:
            raise ValueError(f"Unsupported metric dimension: {dimension}")
        groups: dict[str, list[PreparedHoldoutPrediction]] = {}
        for prediction in self.predictions:
            value = str(getattr(prediction, dimension) or "unknown")
            groups.setdefault(value, []).append(prediction)
        result = {}
        for value, predictions in sorted(groups.items()):
            result[value] = _metrics(predictions)
        return result


def evaluate_prepared_holdout(
    input_paths: Sequence[Path],
    holdout_path: Path,
    feature_set: str = FEATURE_SET_TEXT_WITH_LIGHT_METADATA,
    random_seed: int = 42,
    suspicious_threshold: float = 0.5,
    abstain: bool = False,
) -> PreparedHoldoutResult:
    if feature_set not in {FEATURE_SET_TEXT, FEATURE_SET_TEXT_WITH_LIGHT_METADATA}:
        raise ValueError(f"Unsupported feature set: {feature_set}")
    if not 0.0 <= suspicious_threshold <= 1.0:
        raise ValueError("suspicious_threshold must be between 0.0 and 1.0")

    training_rows = _load_rows(input_paths)
    model = _train_model(_balanced_samples(training_rows, random_seed), feature_set)
    predictions = []
    for line_number, row in enumerate(_load_rows([holdout_path]), start=1):
        label = str(row.get("normalized_label") or "")
        if label not in {NORMALIZED_LABEL_BENIGN, NORMALIZED_LABEL_SUSPICIOUS}:
            raise ValueError(f"unsupported normalized_label on line {line_number}: {label}")
        text = _row_to_text(row, feature_set)
        if abstain:
            probability = float(model.predict_proba([text])[0][list(model.named_steps["classifier"].classes_).index(NORMALIZED_LABEL_SUSPICIOUS)])
            predicted, _ = classify_suspicious_probability(probability)
        else:
            predicted, probability = _predict_label(model, text, suspicious_threshold)
        body_length = len(str(row.get("body_text") or ""))
        predictions.append(PreparedHoldoutPrediction(
            sample_id=str(row.get("sample_id") or f"row-{line_number}"),
            expected_label=label,
            predicted_label=predicted,
            source=str(row.get("source") or "unknown"),
            source_url_flag=str(row.get("metadata", {}).get("source_urls_flag") or "unknown"),
            body_length_bucket=_length_bucket(body_length),
            url_count=len(row.get("urls", [])) if isinstance(row.get("urls"), list) else 0,
            suspicious_probability=probability,
            family=str(row.get("family") or "unclassified"),
        ))
    return PreparedHoldoutResult(predictions=tuple(predictions))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate the baseline against prepared JSONL holdout data.")
    parser.add_argument("--input", action="append", required=True, help="Prepared training JSONL file.")
    parser.add_argument("--holdout", required=True, help="Prepared holdout JSONL file. Keep it outside Git.")
    parser.add_argument("--feature-set", default=FEATURE_SET_TEXT_WITH_LIGHT_METADATA, choices=[FEATURE_SET_TEXT, FEATURE_SET_TEXT_WITH_LIGHT_METADATA])
    parser.add_argument("--random-seed", type=int, default=42)
    parser.add_argument("--suspicious-threshold", type=float, default=0.5)
    parser.add_argument("--abstain", action="store_true", help="Use conservative confidence bands.")
    args = parser.parse_args(argv)
    result = evaluate_prepared_holdout([Path(p) for p in args.input], Path(args.holdout), args.feature_set, args.random_seed, args.suspicious_threshold, args.abstain)
    print_prepared_holdout_result(result)
    return 0


def print_prepared_holdout_result(result: PreparedHoldoutResult) -> None:
    print(f"total: {result.total}")
    print(f"accuracy: {result.accuracy:.4f}")
    print(f"false_positive_benign: {result.false_positive_benign}")
    print(f"false_negative_suspicious: {result.false_negative_suspicious}")
    print(f"inconclusive: {result.inconclusive}")
    print(f"coverage: {result.coverage:.4f}")
    print(f"abstention_rate: {result.abstention_rate:.4f}")
    print(f"conditional_accuracy: {result.conditional_accuracy:.4f}")
    print(f"confident_false_positive_rate: {result.confident_false_positive_rate:.4f}")
    print(f"confident_false_negative_rate: {result.confident_false_negative_rate:.4f}")
    for dimension in ("expected_label", "family", "source_url_flag", "body_length_bucket"):
        print(f"metrics_by_{dimension}:")
        for key, metrics in result.metrics_by(dimension).items():
            print(f"  {key}: {json.dumps(metrics, sort_keys=True)}")


def _load_rows(paths: Sequence[Path]) -> list[dict[str, object]]:
    rows = []
    for path in paths:
        rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return rows


def _row_to_text(row: dict[str, object], feature_set: str) -> str:
    parts = [str(row.get("subject") or ""), str(row.get("body_text") or "")]
    if feature_set == FEATURE_SET_TEXT_WITH_LIGHT_METADATA:
        parts.extend(str(url) for url in row.get("urls", []) if isinstance(url, str))
        parts.extend(str(name) for name in row.get("attachment_filenames", []) if isinstance(name, str))
    return "\n".join(parts)


def _length_bucket(length: int) -> str:
    if length < 300:
        return "short_lt_300"
    if length < 1500:
        return "medium_300_1499"
    return "long_gte_1500"


def _metrics(predictions: list[PreparedHoldoutPrediction]) -> dict[str, float | int]:
    total = len(predictions)
    inconclusive = sum(p.predicted_label == "inconclusive" for p in predictions)
    classified = [p for p in predictions if p.predicted_label != "inconclusive"]
    benign_total = sum(p.expected_label == NORMALIZED_LABEL_BENIGN for p in predictions)
    suspicious_total = sum(p.expected_label == NORMALIZED_LABEL_SUSPICIOUS for p in predictions)
    false_positive = sum(p.expected_label == NORMALIZED_LABEL_BENIGN and p.predicted_label == NORMALIZED_LABEL_SUSPICIOUS for p in predictions)
    false_negative = sum(p.expected_label == NORMALIZED_LABEL_SUSPICIOUS and p.predicted_label == NORMALIZED_LABEL_BENIGN for p in predictions)
    return {
        "total": total,
        "accuracy": sum(p.is_correct for p in predictions) / total if total else 0.0,
        "false_positive_benign": false_positive,
        "false_negative_suspicious": false_negative,
        "coverage": 0.0 if total == 0 else len(classified) / total,
        "abstention_rate": 0.0 if total == 0 else inconclusive / total,
        "conditional_accuracy": 0.0 if not classified else sum(p.is_correct for p in classified) / len(classified),
        "confident_false_positive_rate": 0.0 if benign_total == 0 else false_positive / benign_total,
        "confident_false_negative_rate": 0.0 if suspicious_total == 0 else false_negative / suspicious_total,
    }


if __name__ == "__main__":
    raise SystemExit(main())
