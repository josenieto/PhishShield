# Scope Gate Validation

## Purpose

The scope gate is evaluated separately from the advisory binary classifier.
It decides whether an email belongs to a validated notification family; it
does not decide whether the email is benign or suspicious.

## Fixture Matrix

The fixture manifest is:

```text
config/ml/scope_gate_fixture_manifest.jsonl
```

The matrix contains 32 in-scope PhishShield notification fixtures and five
explicit out-of-scope cases. The current deterministic gate result is:

```text
total: 37
in_scope_recall: 1.0000
scope_accuracy: 1.0000
family_assignment_accuracy: 0.8750
out_of_scope_precision: 1.0000
false_in_scope_rate: 0.0000
```

The gate passes all covered fixtures through and rejects all explicit
out-of-scope cases. Family assignment is not perfect: four fixtures are
assigned to a neighboring operational family. This is acceptable for the
initial routing boundary but blocks treating the gate as a production-grade
family classifier. The binary model remains advisory and the deterministic
analysis remains authoritative.

## External Diagnostic Profiles

CEAS-08 and MeAJOR are not assigned expected families because their source
metadata does not define the PhishShield operational family taxonomy. Their
results therefore report predicted in-scope rate only; family recall and
out-of-scope precision are not meaningful for these datasets.

Current predicted in-scope rates:

| Source | Rows | Predicted in scope | Predicted out of scope |
|---|---:|---:|---:|
| CEAS-08 | 39,154 | 15,523 (`39.64%`) | 23,631 (`60.36%`) |
| MeAJOR English diagnostic subset | 80,968 | 26,645 (`32.90%`) | 54,323 (`67.10%`) |

These figures support the scope-aware interpretation of the earlier low binary
coverage results. They do not establish that every predicted in-scope message
belongs to a correct family, because the external corpora lack reviewed family
labels.

## Evaluation Contract

The evaluator is:

```text
tools/ml_training/evaluate_scope_gate.py
```

It does not load a model artifact or train a classifier. It invokes the same
Application scope function used by the runtime adapter. This keeps scope
validation independent from binary model performance.

Future family-labeled data can add meaningful `family_assignment_accuracy`,
`out_of_scope_precision`, and `false_in_scope_rate` measurements. Future
training may replace the deterministic gate behind the same scope boundary,
but must use separate training, calibration, regression, and promotion data.

## In-Scope Binary Evaluation

The prepared holdout evaluator now applies the same scope gate before binary
classification. Rows classified as `out_of_scope` are reported separately and
are not counted as binary false positives or false negatives. Binary metrics
such as `in_scope_coverage` and `in_scope_conditional_accuracy` apply only to
rows admitted by the gate.

On the current diagnostic runs:

| Source | In-scope rows | In-scope coverage | In-scope conditional accuracy |
|---|---:|---:|---:|
| CEAS-08 | 15,523 (`39.64%`) | `55.78%` | `96.73%` |
| MeAJOR English subset | 26,645 (`32.90%`) | `48.33%` | `96.79%` |

The gate improves interpretation by separating historical/out-of-scope email
from binary model behavior. It does not make either source promotion evidence:
the admitted rows still lack reviewed PhishShield family labels and the
in-scope coverage remains below the approved promotion threshold.
