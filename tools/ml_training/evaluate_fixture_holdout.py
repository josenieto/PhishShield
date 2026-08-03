import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from tools.ml_data_preparation.phishshield_fixtures import (
    NORMALIZED_LABEL_BENIGN,
    NORMALIZED_LABEL_SUSPICIOUS,
    prepare_phishshield_fixture_email,
)
from tools.ml_training.train_baseline import (
    FEATURE_SET_TEXT,
    FEATURE_SET_TEXT_WITH_LIGHT_METADATA,
)
from tools.ml_training.confidence_policy import classify_suspicious_probability


DEFAULT_FIXTURE_LABELS = {
    "benign_account_summary.eml": NORMALIZED_LABEL_BENIGN,
    "benign_account_usage_digest.eml": NORMALIZED_LABEL_BENIGN,
    "benign_account_billing_summary.eml": NORMALIZED_LABEL_BENIGN,
    "benign_invoice_with_pdf.eml": NORMALIZED_LABEL_BENIGN,
    "benign_security_alert_login_notice.eml": NORMALIZED_LABEL_BENIGN,
    "benign_device_login_history.eml": NORMALIZED_LABEL_BENIGN,
    "benign_mfa_enabled_notice.eml": NORMALIZED_LABEL_BENIGN,
    "benign_mfa_recovery_codes_notice.eml": NORMALIZED_LABEL_BENIGN,
    "benign_html_only_newsletter_notice.eml": NORMALIZED_LABEL_BENIGN,
    "benign_html_product_newsletter_account_preferences.eml": NORMALIZED_LABEL_BENIGN,
    "benign_newsletter_security_tips.eml": NORMALIZED_LABEL_BENIGN,
    "benign_cloud_storage_usage_digest.eml": NORMALIZED_LABEL_BENIGN,
    "benign_vendor_invoice_status_update.eml": NORMALIZED_LABEL_BENIGN,
    "benign_hr_benefits_reminder.eml": NORMALIZED_LABEL_BENIGN,
    "benign_support_ticket_update.eml": NORMALIZED_LABEL_BENIGN,
    "benign_support_case_waiting_customer.eml": NORMALIZED_LABEL_BENIGN,
    "suspicious_html_notice.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_shortener_login_notice.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_html_only_credential_lure.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_qr_login_lure.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_cloud_share_auth_failure.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_mfa_push_approval_lure.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_shared_invoice_qr_lure.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_cloud_storage_quota_lure.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_device_login_verification_lure.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_mfa_recovery_codes_lure.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_billing_profile_reauth_lure.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_cloud_storage_expiry_lure.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_vendor_invoice_portal_lure.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_hr_benefits_login_lure.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_support_case_auth_lure.eml": NORMALIZED_LABEL_SUSPICIOUS,
    "suspicious_newsletter_preferences_credential_lure.eml": NORMALIZED_LABEL_SUSPICIOUS,
}


@dataclass(frozen=True)
class HoldoutPrediction:
    fixture_name: str
    expected_label: str
    predicted_label: str
    suspicious_probability: float | None = None
    family: str = "unclassified"
    source: str = "unknown"

    @property
    def is_correct(self) -> bool:
        return self.expected_label == self.predicted_label


@dataclass(frozen=True)
class HoldoutEvaluationResult:
    predictions: tuple[HoldoutPrediction, ...]

    @property
    def total(self) -> int:
        return len(self.predictions)

    @property
    def correct(self) -> int:
        return sum(1 for prediction in self.predictions if prediction.is_correct)

    @property
    def accuracy(self) -> float:
        return 0.0 if self.total == 0 else self.correct / self.total

    @property
    def false_positive_benign(self) -> int:
        return sum(
            1
            for prediction in self.predictions
            if prediction.expected_label == NORMALIZED_LABEL_BENIGN
            and prediction.predicted_label == NORMALIZED_LABEL_SUSPICIOUS
        )

    @property
    def false_negative_suspicious(self) -> int:
        return sum(
            1
            for prediction in self.predictions
            if prediction.expected_label == NORMALIZED_LABEL_SUSPICIOUS
            and prediction.predicted_label == NORMALIZED_LABEL_BENIGN
        )

    @property
    def inconclusive(self) -> int:
        return sum(prediction.predicted_label == "inconclusive" for prediction in self.predictions)

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

    @property
    def metrics_by_family(self) -> dict[str, dict[str, float | int]]:
        metrics: dict[str, dict[str, float | int]] = {}
        for family in sorted({prediction.family for prediction in self.predictions}):
            predictions = [prediction for prediction in self.predictions if prediction.family == family]
            total = len(predictions)
            correct = sum(1 for prediction in predictions if prediction.is_correct)
            benign_total = sum(
                1 for prediction in predictions if prediction.expected_label == NORMALIZED_LABEL_BENIGN
            )
            suspicious_total = sum(
                1 for prediction in predictions if prediction.expected_label == NORMALIZED_LABEL_SUSPICIOUS
            )
            false_positive_benign = sum(
                1
                for prediction in predictions
                if prediction.expected_label == NORMALIZED_LABEL_BENIGN
                and prediction.predicted_label == NORMALIZED_LABEL_SUSPICIOUS
            )
            false_negative_suspicious = sum(
                1
                for prediction in predictions
                if prediction.expected_label == NORMALIZED_LABEL_SUSPICIOUS
                and prediction.predicted_label == NORMALIZED_LABEL_BENIGN
            )
            metrics[family] = {
                "total": total,
                "accuracy": 0.0 if total == 0 else correct / total,
                "benign_total": benign_total,
                "suspicious_total": suspicious_total,
                "false_positive_benign": false_positive_benign,
                "false_negative_suspicious": false_negative_suspicious,
                **_abstention_metrics(predictions, false_positive_benign, false_negative_suspicious),
            }

        return metrics


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate a baseline classifier against PhishShield fixture holdout emails.",
    )
    parser.add_argument("--input", action="append", required=True, help="Prepared training JSONL file. Can be provided multiple times.")
    parser.add_argument("--fixtures-dir", required=True, help="Directory containing PhishShield .eml fixtures.")
    parser.add_argument(
        "--holdout-manifest",
        default=None,
        help="Optional JSONL manifest with path, expected_label, family, and source fields.",
    )
    parser.add_argument(
        "--feature-set",
        default=FEATURE_SET_TEXT,
        choices=[FEATURE_SET_TEXT, FEATURE_SET_TEXT_WITH_LIGHT_METADATA],
    )
    parser.add_argument("--random-seed", type=int, default=42)
    parser.add_argument(
        "--suspicious-threshold",
        type=float,
        default=None,
        help="Optional probability threshold for predicting suspicious fixtures.",
    )
    parser.add_argument("--abstain", action="store_true", help="Use conservative confidence bands.")

    args = parser.parse_args(argv)
    result = evaluate_fixture_holdout(
        input_paths=[Path(input_path) for input_path in args.input],
        fixtures_dir=Path(args.fixtures_dir),
        holdout_manifest=Path(args.holdout_manifest) if args.holdout_manifest else None,
        feature_set=args.feature_set,
        random_seed=args.random_seed,
        suspicious_threshold=args.suspicious_threshold,
        abstain=args.abstain,
    )
    print_holdout_evaluation_result(result)

    return 0


def evaluate_fixture_holdout(
    input_paths: Sequence[Path],
    fixtures_dir: Path,
    feature_set: str = FEATURE_SET_TEXT,
    random_seed: int = 42,
    fixture_labels: dict[str, str] | None = None,
    suspicious_threshold: float | None = None,
    holdout_manifest: Path | None = None,
    abstain: bool = False,
) -> HoldoutEvaluationResult:
    if feature_set not in {FEATURE_SET_TEXT, FEATURE_SET_TEXT_WITH_LIGHT_METADATA}:
        raise ValueError(f"Unsupported feature set: {feature_set}")

    if suspicious_threshold is not None and not 0.0 <= suspicious_threshold <= 1.0:
        raise ValueError("suspicious_threshold must be between 0.0 and 1.0")

    training_samples = _balanced_samples(_load_samples(input_paths), random_seed=random_seed)
    model = _train_model(training_samples, feature_set=feature_set)
    predictions: list[HoldoutPrediction] = []

    holdout_rows = (
        _load_holdout_manifest(holdout_manifest)
        if holdout_manifest is not None
        else [
            {"path": fixture_name, "expected_label": expected_label, "family": "unclassified", "source": "phishshield-fixtures"}
            for fixture_name, expected_label in (DEFAULT_FIXTURE_LABELS if fixture_labels is None else fixture_labels).items()
        ]
    )

    for holdout_row in holdout_rows:
        fixture_name = str(holdout_row["path"])
        expected_label = str(holdout_row["expected_label"])
        fixture_path = Path(fixture_name)
        if not fixture_path.is_absolute():
            fixture_path = fixtures_dir / fixture_path
        if not fixture_path.is_file():
            raise ValueError(f"fixture does not exist: {fixture_path}")

        sample = prepare_phishshield_fixture_email(
            raw_email=fixture_path.read_bytes(),
            source_id=fixture_name,
            normalized_label=expected_label,
        )
        fixture_text = _sample_to_text(_sample_to_dict(sample), feature_set=feature_set)
        if abstain:
            classifier = model.named_steps["classifier"]
            suspicious_index = list(classifier.classes_).index(NORMALIZED_LABEL_SUSPICIOUS)
            suspicious_probability = float(model.predict_proba([fixture_text])[0][suspicious_index])
            predicted_label, _ = classify_suspicious_probability(suspicious_probability)
        else:
            predicted_label, suspicious_probability = _predict_label(
                model=model,
                fixture_text=fixture_text,
                suspicious_threshold=suspicious_threshold,
            )
        predictions.append(
            HoldoutPrediction(
                fixture_name=fixture_name,
                expected_label=expected_label,
                predicted_label=predicted_label,
                suspicious_probability=suspicious_probability,
                family=str(holdout_row.get("family", "unclassified")),
                source=str(holdout_row.get("source", "unknown")),
            )
        )

    return HoldoutEvaluationResult(predictions=tuple(predictions))


def print_holdout_evaluation_result(result: HoldoutEvaluationResult) -> None:
    for prediction in result.predictions:
        print(f"fixture: {prediction.fixture_name}")
        print(f"expected: {prediction.expected_label}")
        print(f"predicted: {prediction.predicted_label}")
        if prediction.suspicious_probability is not None:
            print(f"suspicious_probability: {prediction.suspicious_probability:.4f}")
        print(f"correct: {str(prediction.is_correct).lower()}")
        print(f"family: {prediction.family}")
        print(f"source: {prediction.source}")
        print()

    print("summary:")
    print(f"total: {result.total}")
    print(f"correct: {result.correct}")
    print(f"accuracy: {result.accuracy:.4f}")
    print(f"false_positive_benign: {result.false_positive_benign}")
    print(f"false_negative_suspicious: {result.false_negative_suspicious}")
    print(f"inconclusive: {result.inconclusive}")
    print(f"coverage: {result.coverage:.4f}")
    print(f"abstention_rate: {result.abstention_rate:.4f}")
    print(f"conditional_accuracy: {result.conditional_accuracy:.4f}")
    print(f"confident_false_positive_rate: {result.confident_false_positive_rate:.4f}")
    print(f"confident_false_negative_rate: {result.confident_false_negative_rate:.4f}")
    print("metrics_by_family:")
    for family, metrics in result.metrics_by_family.items():
        print(f"  {family}: {json.dumps(metrics, sort_keys=True)}")


def _predict_label(
    model: Pipeline,
    fixture_text: str,
    suspicious_threshold: float | None,
) -> tuple[str, float | None]:
    if suspicious_threshold is None:
        return str(model.predict([fixture_text])[0]), None

    suspicious_probability = _predict_suspicious_probability(model, fixture_text)
    predicted_label = (
        NORMALIZED_LABEL_SUSPICIOUS
        if suspicious_probability >= suspicious_threshold
        else NORMALIZED_LABEL_BENIGN
    )

    return predicted_label, suspicious_probability


def _abstention_metrics(
    predictions: list[HoldoutPrediction],
    false_positive: int,
    false_negative: int,
) -> dict[str, float]:
    total = len(predictions)
    classified = [p for p in predictions if p.predicted_label != "inconclusive"]
    benign_total = sum(p.expected_label == NORMALIZED_LABEL_BENIGN for p in predictions)
    suspicious_total = sum(p.expected_label == NORMALIZED_LABEL_SUSPICIOUS for p in predictions)
    return {
        "coverage": 0.0 if total == 0 else len(classified) / total,
        "abstention_rate": 0.0 if total == 0 else (total - len(classified)) / total,
        "conditional_accuracy": 0.0 if not classified else sum(p.is_correct for p in classified) / len(classified),
        "confident_false_positive_rate": 0.0 if benign_total == 0 else false_positive / benign_total,
        "confident_false_negative_rate": 0.0 if suspicious_total == 0 else false_negative / suspicious_total,
    }


def _predict_suspicious_probability(model: Pipeline, fixture_text: str) -> float:
    classifier = model.named_steps["classifier"]
    classes = list(classifier.classes_)
    suspicious_index = classes.index(NORMALIZED_LABEL_SUSPICIOUS)

    return float(model.predict_proba([fixture_text])[0][suspicious_index])


def _train_model(samples: list[dict[str, object]], feature_set: str) -> Pipeline:
    texts = [_sample_to_text(sample, feature_set=feature_set) for sample in samples]
    labels = [sample["normalized_label"] for sample in samples]
    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("classifier", LogisticRegression(max_iter=1_000)),
        ]
    )
    model.fit(texts, labels)

    return model


def _load_samples(input_paths: Sequence[Path]) -> list[dict[str, object]]:
    samples: list[dict[str, object]] = []

    for input_path in input_paths:
        for line in input_path.read_text(encoding="utf-8").split("\n"):
            if line.strip():
                samples.append(json.loads(line))

    return samples


def _load_holdout_manifest(manifest_path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line_number, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        required_fields = {"path", "expected_label", "family", "source"}
        missing_fields = required_fields - row.keys()
        if missing_fields:
            raise ValueError(
                f"holdout manifest line {line_number} is missing: {', '.join(sorted(missing_fields))}"
            )
        if row["expected_label"] not in {NORMALIZED_LABEL_BENIGN, NORMALIZED_LABEL_SUSPICIOUS}:
            raise ValueError(f"unsupported holdout label on line {line_number}: {row['expected_label']}")
        rows.append(row)

    if not rows:
        raise ValueError("holdout manifest must contain at least one row")

    return rows


def _balanced_samples(samples: list[dict[str, object]], random_seed: int) -> list[dict[str, object]]:
    benign_samples = [sample for sample in samples if sample.get("normalized_label") == NORMALIZED_LABEL_BENIGN]
    suspicious_samples = [sample for sample in samples if sample.get("normalized_label") == NORMALIZED_LABEL_SUSPICIOUS]
    target_size = min(len(benign_samples), len(suspicious_samples))

    if target_size < 2:
        raise ValueError("at least two benign and two suspicious samples are required")

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


def _sample_to_dict(sample) -> dict[str, object]:
    return {
        "subject": sample.subject,
        "body_text": sample.body_text,
        "urls": list(sample.urls),
        "attachment_filenames": list(sample.attachment_filenames),
    }


if __name__ == "__main__":
    raise SystemExit(main())
