import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


FEATURE_SET_TEXT = "text"
FEATURE_SET_TEXT_WITH_LIGHT_METADATA = "text_with_light_metadata"
STRATEGY_BALANCED = "balanced"


class TrainingResult:
    def __init__(
        self,
        total_samples: int,
        train_samples: int,
        validation_samples: int,
        label_distribution: Counter[str],
        accuracy: float,
        precision_suspicious: float,
        recall_suspicious: float,
        f1_suspicious: float,
        confusion_matrix_values: list[list[int]],
    ) -> None:
        self.total_samples = total_samples
        self.train_samples = train_samples
        self.validation_samples = validation_samples
        self.label_distribution = label_distribution
        self.accuracy = accuracy
        self.precision_suspicious = precision_suspicious
        self.recall_suspicious = recall_suspicious
        self.f1_suspicious = f1_suspicious
        self.confusion_matrix_values = confusion_matrix_values


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Train a local baseline classifier from prepared PhishShield JSONL samples.",
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

    args = parser.parse_args(argv)
    result = train_baseline(
        input_paths=[Path(input_path) for input_path in args.input],
        strategy=args.strategy,
        feature_set=args.feature_set,
        validation_ratio=args.validation_ratio,
        random_seed=args.random_seed,
    )
    print_training_result(result)

    return 0


def train_baseline(
    input_paths: Sequence[Path],
    strategy: str = STRATEGY_BALANCED,
    feature_set: str = FEATURE_SET_TEXT,
    validation_ratio: float = 0.2,
    random_seed: int = 42,
) -> TrainingResult:
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

    return TrainingResult(
        total_samples=len(balanced_samples),
        train_samples=len(train_texts),
        validation_samples=len(validation_texts),
        label_distribution=label_distribution,
        accuracy=accuracy_score(validation_labels, predictions),
        precision_suspicious=precision[0],
        recall_suspicious=recall[0],
        f1_suspicious=f1[0],
        confusion_matrix_values=confusion_matrix(
            validation_labels,
            predictions,
            labels=["benign", "suspicious"],
        ).tolist(),
    )


def print_training_result(result: TrainingResult) -> None:
    print(f"samples: {result.total_samples}")
    print(f"train_samples: {result.train_samples}")
    print(f"validation_samples: {result.validation_samples}")
    print("labels:")
    for label, count in sorted(result.label_distribution.items()):
        print(f"  {label}: {count}")
    print(f"accuracy: {result.accuracy:.4f}")
    print(f"precision_suspicious: {result.precision_suspicious:.4f}")
    print(f"recall_suspicious: {result.recall_suspicious:.4f}")
    print(f"f1_suspicious: {result.f1_suspicious:.4f}")
    print("confusion_matrix_labels: benign,suspicious")
    print(f"confusion_matrix: {result.confusion_matrix_values}")


def _load_samples(input_paths: Sequence[Path]) -> list[dict[str, object]]:
    samples: list[dict[str, object]] = []

    for input_path in input_paths:
        for line in input_path.read_text(encoding="utf-8").split("\n"):
            if line.strip():
                samples.append(json.loads(line))

    return samples


def _balanced_samples(samples: list[dict[str, object]], random_seed: int) -> list[dict[str, object]]:
    benign_samples = [sample for sample in samples if sample.get("normalized_label") == "benign"]
    suspicious_samples = [sample for sample in samples if sample.get("normalized_label") == "suspicious"]
    target_size = min(len(benign_samples), len(suspicious_samples))

    if target_size < 2:
        raise ValueError("at least two benign and two suspicious samples are required")

    import random

    random_generator = random.Random(random_seed)
    random_generator.shuffle(benign_samples)
    random_generator.shuffle(suspicious_samples)

    return benign_samples[:target_size] + suspicious_samples[:target_size]


def _sample_to_text(sample: dict[str, object], feature_set: str) -> str:
    text_parts = [str(sample.get("subject", "")), str(sample.get("body_text", ""))]

    if feature_set == FEATURE_SET_TEXT_WITH_LIGHT_METADATA:
        text_parts.extend(str(url) for url in sample.get("urls", []) if isinstance(url, str))
        text_parts.extend(
            str(filename)
            for filename in sample.get("attachment_filenames", [])
            if isinstance(filename, str)
        )

    return "\n".join(text_parts)


if __name__ == "__main__":
    raise SystemExit(main())
