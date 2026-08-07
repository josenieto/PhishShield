# Experimental Advisory Inference

## Closure Decision

The scope-aware advisory inference phase is complete as an experimental
capability. Its status is:

```text
status: experimental_advisory
promotion_status: not_approved
```

The deterministic email analysis path remains authoritative. The advisory
branch is optional, disabled by default, local, and must not change findings,
evidence, explanations, or `risk_score`.

## Runtime Flow

```text
raw .eml
  -> deterministic parser representation
  -> deterministic scope/family gate
      -> out_of_scope -> inconclusive (reason: out_of_scope)
      -> covered family -> binary advisory model
          -> benign / suspicious
          -> inconclusive (reason: low_binary_confidence)
```

The current model is a TF-IDF plus Logistic Regression baseline. It is not a
universal phishing classifier. It operates only after the scope gate identifies
one of these notification families:

- account;
- MFA and security;
- cloud and document sharing;
- billing and invoices;
- support;
- HR;
- vendor portals;
- newsletter and account preferences.

The structured API field `abstention_reason` distinguishes scope rejection from
binary uncertainty. The public label remains `inconclusive` for both cases.

## Evidence

The internal fixture and external diagnostic results are recorded in:

- `docs/ML_SCOPE_GATE_VALIDATION.md`;
- `docs/ML_TRAINING_EVALUATION_STRATEGY.md`;
- `docs/ML_PROMOTION_HOLDOUT_CURATION_ASSESSMENT.md`.

The scope gate passes the current fixture matrix with full in-scope recall and
full out-of-scope precision, while family assignment remains imperfect. CEAS-08
and MeAJOR show that the scope gate removes a large historical/out-of-scope
portion before binary evaluation. Their admitted traffic still has insufficient
coverage for product promotion and neither source is independent promotion
evidence.

## Local Configuration

The endpoint is:

```text
POST /analyze-email-model-assessment
```

It is disabled unless all model settings are configured:

```text
PHISHSHIELD_MODEL_ASSESSMENT_ENABLED=true
PHISHSHIELD_MODEL_ARTIFACT_PATH=path/to/model.joblib
PHISHSHIELD_MODEL_METADATA_PATH=path/to/model.metadata.json
```

Artifacts, datasets, predictions, and detailed evaluation outputs remain
outside Git.

## Reproducible Evaluation

Scope-only evaluation:

```text
python -m tools.ml_training.evaluate_scope_gate --fixtures-dir tests/fixtures/emails --fixture-manifest config/ml/scope_gate_fixture_manifest.jsonl
python -m tools.ml_training.evaluate_scope_gate --prepared path/to/ceas_08.jsonl
python -m tools.ml_training.evaluate_scope_gate --prepared path/to/meajor_diagnostic.jsonl
```

Binary evaluation with the scope gate:

```text
python -m tools.ml_training.evaluate_prepared_holdout --input path/to/training.jsonl --holdout path/to/holdout.jsonl --feature-set text_with_light_metadata --abstain
```

## Future Training Path

This closure does not prohibit future model training. It defines the boundary
future work must preserve:

```text
authorized family data
  -> separate training/calibration/regression/promotion roles
  -> family-labeled scope evaluation
  -> family-specific binary model or trained scope gate
  -> temporal and independent validation
  -> explicit scope/version update
```

Future external or corporate data may be used when provenance, licensing,
privacy, deduplication, and role separation are documented. A dataset used for
training or calibration cannot later be presented as independent promotion
evidence.

Product-ready advisory inference remains deferred until authorized,
family-level, independent evidence meets the approved promotion thresholds.
