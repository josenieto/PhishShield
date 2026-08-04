import json
from pathlib import Path

from tools.ml_training.evaluate_scope_gate import evaluate_prepared_scope, evaluate_fixture_scope


def test_should_report_scope_metrics_for_prepared_rows(tmp_path: Path) -> None:
    path = tmp_path / "prepared.jsonl"
    path.write_text(
        "\n".join(
            json.dumps(row)
            for row in (
                {"sample_id": "in", "subject": "Account summary", "body_text": "Review your account activity.", "urls": [], "attachment_filenames": [], "source": "test"},
                {"sample_id": "out", "subject": "Team lunch", "body_text": "Friday lunch is scheduled.", "urls": [], "attachment_filenames": [], "source": "test"},
            )
        )
        + "\n",
        encoding="utf-8",
    )

    result = evaluate_prepared_scope(path)

    assert result.total == 2
    assert result.predicted_in_scope == 1
    assert result.predicted_out_of_scope == 1
    assert result.predicted_in_scope_rate == 0.5
    assert result.scope_accuracy == 0.0
    assert result.reason_distribution == {"in_scope_family": 1, "no_family_signal": 1}


def test_should_evaluate_fixture_manifest_with_expected_families(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "account.eml").write_text(
        "From: sender@example.com\nSubject: Account summary\nContent-Type: text/plain\n\nReview your account activity.",
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text(
        json.dumps({"path": "account.eml", "expected_family": "account", "source": "test"}) + "\n",
        encoding="utf-8",
    )

    result = evaluate_fixture_scope(fixtures, manifest)

    assert result.in_scope_recall == 1.0
    assert result.family_assignment_accuracy == 1.0
