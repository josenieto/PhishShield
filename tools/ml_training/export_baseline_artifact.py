import argparse
import json
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Sequence

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from tools.ml_training.train_baseline import (
    FEATURE_SET_TEXT,
    FEATURE_SET_TEXT_WITH_LIGHT_METADATA,
    STRATEGY_BALANCED,
    _balanced_samples,
    _load_samples,
    _sample_to_text,
)


MODEL_NAME = "phishshield_baseline_candidate"
MODEL_TYPE = "tfidf_logistic_regression"
MODEL_STATUS = "experimental"
HOLDOUT_NAME = "PhishShield 32-fixture notification holdout"
SCOPE_GATE_NAME = "deterministic_v1"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export the selected experimental baseline classifier artifact outside Git.",
    )
    parser.add_argument("--input", action="append", required=True, help="Prepared JSONL file. Can be provided multiple times.")
    parser.add_argument("--strategy", default=STRATEGY_BALANCED, choices=[STRATEGY_BALANCED])
    parser.add_argument(
        "--feature-set",
        default=FEATURE_SET_TEXT,
        choices=[FEATURE_SET_TEXT, FEATURE_SET_TEXT_WITH_LIGHT_METADATA],
    )
    parser.add_argument("--validation-ratio", type=float, default=0.2)
    parser.add_argument("--random-seed", type=int, default=42)
    parser.add_argument("--model-output", required=True, help="Output model artifact path. Keep this outside Git.")
    parser.add_argument("--metadata-output", required=True, help="Output metadata JSON path. Keep this outside Git.")
    parser.add_argument("--holdout-accuracy", type=float, default=None)
    parser.add_argument("--holdout-false-positive-benign", type=int, default=None)
    parser.add_argument("--holdout-false-negative-suspicious", type=int, default=None)

    args = parser.parse_args(argv)
    result = export_baseline_artifact(
        input_paths=[Path(input_path) for input_path in args.input],
        model_output_path=Path(args.model_output),
        metadata_output_path=Path(args.metadata_output),
        strategy=args.strategy,
        feature_set=args.feature_set,
        validation_ratio=args.validation_ratio,
        random_seed=args.random_seed,
        holdout_accuracy=args.holdout_accuracy,
        holdout_false_positive_benign=args.holdout_false_positive_benign,
        holdout_false_negative_suspicious=args.holdout_false_negative_suspicious,
    )
    print_export_result(result)

    return 0


class ExportResult:
    def __init__(
        self,
        model_output_path: Path,
        metadata_output_path: Path,
        samples: int,
        train_samples: int,
        validation_samples: int,
        label_distribution: Counter[str],
        accuracy: float,
        precision_suspicious: float,
        recall_suspicious: float,
        f1_suspicious: float,
    ) -> None:
        self.model_output_path = model_output_path
        self.metadata_output_path = metadata_output_path
        self.samples = samples
        self.train_samples = train_samples
        self.validation_samples = validation_samples
        self.label_distribution = label_distribution
        self.accuracy = accuracy
        self.precision_suspicious = precision_suspicious
        self.recall_suspicious = recall_suspicious
        self.f1_suspicious = f1_suspicious


def export_baseline_artifact(
    input_paths: Sequence[Path],
    model_output_path: Path,
    metadata_output_path: Path,
    strategy: str = STRATEGY_BALANCED,
    feature_set: str = FEATURE_SET_TEXT_WITH_LIGHT_METADATA,
    validation_ratio: float = 0.2,
    random_seed: int = 42,
    holdout_accuracy: float | None = None,
    holdout_false_positive_benign: int | None = None,
    holdout_false_negative_suspicious: int | None = None,
) -> ExportResult:
    if strategy != STRATEGY_BALANCED:
        raise ValueError(f"Unsupported training strategy: {strategy}")

    if feature_set not in {FEATURE_SET_TEXT, FEATURE_SET_TEXT_WITH_LIGHT_METADATA}:
        raise ValueError(f"Unsupported feature set: {feature_set}")

    if not 0.0 < validation_ratio < 1.0:
        raise ValueError("validation_ratio must be between 0.0 and 1.0")

    samples = _load_samples(input_paths)
    balanced_samples = _balanced_samples(samples, random_seed=random_seed)
    label_distribution = Counter(sample["normalized_label"] for sample in balanced_samples)
    texts = [_sample_to_text(sample, feature_set=feature_set) for sample in balanced_samples]
    labels = [sample["normalized_label"] for sample in balanced_samples]
    train_texts, validation_texts, train_labels, validation_labels = train_test_split(
        texts,
        labels,
        test_size=validation_ratio,
        random_state=random_seed,
        stratify=labels,
    )
    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("classifier", LogisticRegression(max_iter=1_000)),
        ]
    )
    model.fit(train_texts, train_labels)
    predictions = model.predict(validation_texts)
    precision, recall, f1, _ = precision_recall_fscore_support(
        validation_labels,
        predictions,
        labels=["suspicious"],
        zero_division=0,
    )
    confusion_matrix_values = confusion_matrix(
        validation_labels,
        predictions,
        labels=["benign", "suspicious"],
    ).tolist()

    model_output_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_output_path)
    metadata = _build_metadata(
        input_paths=input_paths,
        strategy=strategy,
        feature_set=feature_set,
        validation_ratio=validation_ratio,
        random_seed=random_seed,
        total_samples=len(balanced_samples),
        train_samples=len(train_texts),
        validation_samples=len(validation_texts),
        label_distribution=label_distribution,
        accuracy=accuracy_score(validation_labels, predictions),
        precision_suspicious=precision[0],
        recall_suspicious=recall[0],
        f1_suspicious=f1[0],
        confusion_matrix_values=confusion_matrix_values,
        holdout_accuracy=holdout_accuracy,
        holdout_false_positive_benign=holdout_false_positive_benign,
        holdout_false_negative_suspicious=holdout_false_negative_suspicious,
    )
    metadata_output_path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")

    return ExportResult(
        model_output_path=model_output_path,
        metadata_output_path=metadata_output_path,
        samples=len(balanced_samples),
        train_samples=len(train_texts),
        validation_samples=len(validation_texts),
        label_distribution=label_distribution,
        accuracy=accuracy_score(validation_labels, predictions),
        precision_suspicious=precision[0],
        recall_suspicious=recall[0],
        f1_suspicious=f1[0],
    )


def print_export_result(result: ExportResult) -> None:
    print(f"model_output: {result.model_output_path}")
    print(f"metadata_output: {result.metadata_output_path}")
    print(f"samples: {result.samples}")
    print(f"train_samples: {result.train_samples}")
    print(f"validation_samples: {result.validation_samples}")
    print("labels:")
    for label, count in sorted(result.label_distribution.items()):
        print(f"  {label}: {count}")
    print(f"accuracy: {result.accuracy:.4f}")
    print(f"precision_suspicious: {result.precision_suspicious:.4f}")
    print(f"recall_suspicious: {result.recall_suspicious:.4f}")
    print(f"f1_suspicious: {result.f1_suspicious:.4f}")


def _build_metadata(
    input_paths: Sequence[Path],
    strategy: str,
    feature_set: str,
    validation_ratio: float,
    random_seed: int,
    total_samples: int,
    train_samples: int,
    validation_samples: int,
    label_distribution: Counter[str],
    accuracy: float,
    precision_suspicious: float,
    recall_suspicious: float,
    f1_suspicious: float,
    confusion_matrix_values: list[list[int]],
    holdout_accuracy: float | None,
    holdout_false_positive_benign: int | None,
    holdout_false_negative_suspicious: int | None,
) -> dict[str, object]:
    return {
        "model_name": MODEL_NAME,
        "model_type": MODEL_TYPE,
        "status": MODEL_STATUS,
        "created_at": datetime.now(UTC).isoformat(),
        "git_commit": _current_git_commit(),
        "feature_set": feature_set,
        "scope_gate": SCOPE_GATE_NAME,
        "covered_families": [
            "account",
            "mfa_security",
            "cloud_document_sharing",
            "billing_invoices",
            "support",
            "hr",
            "vendor_portals",
            "newsletter_preferences",
        ],
        "abstention_policy": {
            "high_confidence_threshold": 0.85,
            "out_of_scope_reason": "out_of_scope",
            "low_binary_confidence_reason": "low_binary_confidence",
        },
        "diagnostic_sources": ["CEAS-08", "MeAJOR", "Darkknight"],
        "promotion_status": "not_approved",
        "strategy": strategy,
        "validation_ratio": validation_ratio,
        "random_seed": random_seed,
        "training_inputs": [str(input_path) for input_path in input_paths],
        "samples": total_samples,
        "train_samples": train_samples,
        "validation_samples": validation_samples,
        "label_distribution": dict(sorted(label_distribution.items())),
        "metrics": {
            "accuracy": accuracy,
            "precision_suspicious": precision_suspicious,
            "recall_suspicious": recall_suspicious,
            "f1_suspicious": f1_suspicious,
        },
        "confusion_matrix_labels": ["benign", "suspicious"],
        "confusion_matrix": confusion_matrix_values,
        "holdout_reference": {
            "name": HOLDOUT_NAME,
            "accuracy": holdout_accuracy,
            "false_positive_benign": holdout_false_positive_benign,
            "false_negative_suspicious": holdout_false_negative_suspicious,
        },
        "limitations": [
            "Experimental artifact only.",
            "Not production-ready.",
            "Uses synthetic calibration data.",
            "No non-synthetic notification validation yet.",
            "Scope-aware advisory inference is experimental only.",
            "External diagnostic sources are not promotion evidence.",
            "Deterministic analysis remains authoritative.",
            "Runtime inference integration remains deferred.",
            "Runtime inference is experimental, optional, and disabled by default.",
        ],
    }


def _current_git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return "unknown"

    return result.stdout.strip()


if __name__ == "__main__":
    raise SystemExit(main())
