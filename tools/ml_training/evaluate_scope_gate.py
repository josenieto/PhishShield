"""Evaluate the deterministic advisory scope gate without loading a model."""

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from application.models.extracted_email import ExtractedEmailContent
from application.models.scope_assessment import (
    SCOPE_FAMILY_OUT_OF_SCOPE,
    ScopeAssessment,
    assess_email_scope,
)
from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


@dataclass(frozen=True)
class ScopePrediction:
    sample_id: str
    predicted_family: str
    predicted_reason: str
    expected_family: str | None = None
    source: str = "unknown"
    body_length_bucket: str = "unknown"


@dataclass(frozen=True)
class ScopeEvaluationResult:
    predictions: tuple[ScopePrediction, ...]

    @property
    def total(self) -> int:
        return len(self.predictions)

    @property
    def expected_in_scope(self) -> int:
        return sum(self._is_expected_in_scope(p) for p in self.predictions)

    @property
    def expected_out_of_scope(self) -> int:
        return sum(self._is_expected_out_of_scope(p) for p in self.predictions)

    @property
    def predicted_in_scope(self) -> int:
        return sum(p.predicted_family != SCOPE_FAMILY_OUT_OF_SCOPE for p in self.predictions)

    @property
    def predicted_out_of_scope(self) -> int:
        return sum(p.predicted_family == SCOPE_FAMILY_OUT_OF_SCOPE for p in self.predictions)

    @property
    def predicted_in_scope_rate(self) -> float:
        return _ratio(self.predicted_in_scope, self.total)

    @property
    def correct_scope_predictions(self) -> int:
        return sum(
            self._is_expected_in_scope(p) and p.predicted_family != SCOPE_FAMILY_OUT_OF_SCOPE
            or self._is_expected_out_of_scope(p) and p.predicted_family == SCOPE_FAMILY_OUT_OF_SCOPE
            for p in self.predictions
        )

    @property
    def in_scope_recall(self) -> float:
        return _ratio(self._correct_in_scope_predictions(), self.expected_in_scope)

    @property
    def family_assignment_accuracy(self) -> float:
        return _ratio(
            sum(
                p.expected_family == p.predicted_family
                for p in self.predictions
                if self._is_expected_in_scope(p) and p.predicted_family != SCOPE_FAMILY_OUT_OF_SCOPE
            ),
            self.expected_in_scope,
        )

    @property
    def scope_accuracy(self) -> float:
        return _ratio(self.correct_scope_predictions, self.total)

    @property
    def out_of_scope_precision(self) -> float:
        return _ratio(self._correct_out_of_scope_predictions(), self.predicted_out_of_scope)

    @property
    def false_in_scope_rate(self) -> float:
        return _ratio(
            sum(self._is_expected_out_of_scope(p) and p.predicted_family != SCOPE_FAMILY_OUT_OF_SCOPE for p in self.predictions),
            self.expected_out_of_scope,
        )

    @property
    def reason_distribution(self) -> dict[str, int]:
        return dict(sorted(Counter(p.predicted_reason for p in self.predictions).items()))

    def metrics_by(self, dimension: str) -> dict[str, dict[str, float | int]]:
        if dimension not in {"source", "body_length_bucket", "predicted_family"}:
            raise ValueError(f"Unsupported scope metric dimension: {dimension}")
        groups: dict[str, list[ScopePrediction]] = {}
        for prediction in self.predictions:
            groups.setdefault(str(getattr(prediction, dimension)), []).append(prediction)
        return {key: _group_metrics(values) for key, values in sorted(groups.items())}

    def _is_expected_in_scope(self, prediction: ScopePrediction) -> bool:
        return prediction.expected_family not in {None, SCOPE_FAMILY_OUT_OF_SCOPE}

    def _is_expected_out_of_scope(self, prediction: ScopePrediction) -> bool:
        return prediction.expected_family == SCOPE_FAMILY_OUT_OF_SCOPE

    def _correct_in_scope_predictions(self) -> int:
        return sum(self._is_expected_in_scope(p) and p.predicted_family != SCOPE_FAMILY_OUT_OF_SCOPE for p in self.predictions)

    def _correct_out_of_scope_predictions(self) -> int:
        return sum(self._is_expected_out_of_scope(p) and p.predicted_family == SCOPE_FAMILY_OUT_OF_SCOPE for p in self.predictions)


def evaluate_fixture_scope(
    fixtures_dir: Path,
    manifest_path: Path,
) -> ScopeEvaluationResult:
    extractor = PythonEmailContentExtractorAdapter()
    predictions: list[ScopePrediction] = []
    for row in _load_jsonl(manifest_path):
        fixture_path = Path(str(row["path"]))
        if not fixture_path.is_absolute():
            fixture_path = fixtures_dir / fixture_path
        if not fixture_path.is_file():
            raise ValueError(f"fixture does not exist: {fixture_path}")
        extracted = extractor.extract(fixture_path.read_bytes())
        scope = assess_email_scope(extracted)
        predictions.append(_prediction(str(row["path"]), scope, row.get("expected_family"), row.get("source")))
    return ScopeEvaluationResult(tuple(predictions))


def evaluate_prepared_scope(holdout_path: Path) -> ScopeEvaluationResult:
    predictions: list[ScopePrediction] = []
    for line_number, row in enumerate(_load_jsonl(holdout_path), start=1):
        subject = str(row.get("subject") or "")
        body = str(row.get("body_text") or "")
        urls = tuple(value for value in row.get("urls", []) if isinstance(value, str))
        attachments = tuple(value for value in row.get("attachment_filenames", []) if isinstance(value, str))
        extracted = ExtractedEmailContent("", urls, attachments, subject, body, "unknown", "unknown", "unknown")
        scope = assess_email_scope(extracted)
        predictions.append(_prediction(str(row.get("sample_id") or f"row-{line_number}"), scope, None, row.get("source"), body))
    return ScopeEvaluationResult(tuple(predictions))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate the deterministic advisory scope gate.")
    parser.add_argument("--fixtures-dir")
    parser.add_argument("--fixture-manifest")
    parser.add_argument("--prepared")
    args = parser.parse_args(argv)
    if bool(args.fixture_manifest) != bool(args.fixtures_dir) or bool(args.prepared) == bool(args.fixture_manifest):
        parser.error("provide either --prepared or both --fixtures-dir and --fixture-manifest")
    result = (
        evaluate_prepared_scope(Path(args.prepared))
        if args.prepared
        else evaluate_fixture_scope(Path(args.fixtures_dir), Path(args.fixture_manifest))
    )
    print_scope_evaluation(result)
    return 0


def print_scope_evaluation(result: ScopeEvaluationResult) -> None:
    print(f"total: {result.total}")
    print(f"expected_in_scope: {result.expected_in_scope}")
    print(f"expected_out_of_scope: {result.expected_out_of_scope}")
    print(f"predicted_in_scope: {result.predicted_in_scope}")
    print(f"predicted_out_of_scope: {result.predicted_out_of_scope}")
    print(f"predicted_in_scope_rate: {result.predicted_in_scope_rate:.4f}")
    print(f"in_scope_recall: {result.in_scope_recall:.4f}")
    print(f"scope_accuracy: {result.scope_accuracy:.4f}")
    print(f"family_assignment_accuracy: {result.family_assignment_accuracy:.4f}")
    print(f"out_of_scope_precision: {result.out_of_scope_precision:.4f}")
    print(f"false_in_scope_rate: {result.false_in_scope_rate:.4f}")
    print(f"reason_distribution: {json.dumps(result.reason_distribution, sort_keys=True)}")
    for dimension in ("source", "body_length_bucket", "predicted_family"):
        print(f"metrics_by_{dimension}:")
        for key, metrics in result.metrics_by(dimension).items():
            print(f"  {key}: {json.dumps(metrics, sort_keys=True)}")


def _prediction(
    sample_id: str,
    scope: ScopeAssessment,
    expected_family: object,
    source: object,
    body: str = "",
) -> ScopePrediction:
    return ScopePrediction(
        sample_id=sample_id,
        predicted_family=scope.family,
        predicted_reason=scope.reason,
        expected_family=str(expected_family) if expected_family is not None else None,
        source=str(source or "unknown"),
        body_length_bucket=_length_bucket(len(body)),
    )


def _group_metrics(predictions: list[ScopePrediction]) -> dict[str, float | int]:
    expected_in_scope = sum(p.expected_family not in {None, SCOPE_FAMILY_OUT_OF_SCOPE} for p in predictions)
    expected_out = sum(p.expected_family == SCOPE_FAMILY_OUT_OF_SCOPE for p in predictions)
    predicted_out = sum(p.predicted_family == SCOPE_FAMILY_OUT_OF_SCOPE for p in predictions)
    correct_in = sum(p.expected_family not in {None, SCOPE_FAMILY_OUT_OF_SCOPE} and p.predicted_family != SCOPE_FAMILY_OUT_OF_SCOPE for p in predictions)
    correct_out = sum(p.expected_family == SCOPE_FAMILY_OUT_OF_SCOPE and p.predicted_family == SCOPE_FAMILY_OUT_OF_SCOPE for p in predictions)
    family_correct = sum(p.expected_family == p.predicted_family for p in predictions if p.expected_family not in {None, SCOPE_FAMILY_OUT_OF_SCOPE} and p.predicted_family != SCOPE_FAMILY_OUT_OF_SCOPE)
    return {
        "total": len(predictions),
        "in_scope_recall": _ratio(correct_in, expected_in_scope),
        "family_assignment_accuracy": _ratio(family_correct, expected_in_scope),
        "out_of_scope_precision": _ratio(correct_out, predicted_out),
        "false_in_scope_rate": _ratio(expected_out - correct_out, expected_out),
    }


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _length_bucket(length: int) -> str:
    if length < 300:
        return "short_lt_300"
    if length < 1500:
        return "medium_300_1499"
    return "long_gte_1500"


def _ratio(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


if __name__ == "__main__":
    raise SystemExit(main())
