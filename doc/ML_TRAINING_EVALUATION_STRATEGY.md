# ML Training And Evaluation Strategy

## Purpose

This document defines the first training and evaluation strategy for a future PhishShield-owned email classification model.

It builds on:

- `doc/ML_DATASET_RESEARCH.md`
- `doc/ML_DATA_PREPARATION_PLAN.md`
- `doc/MODEL_ASSISTED_ANALYSIS_PLAN.md`

This document also records the first baseline training command once it is introduced. It still does not introduce model artifacts, runtime dependencies, or inference adapters.

---

## Strategy Summary

The first model experiment should be a simple binary classifier:

```text
benign vs suspicious
```

The first baseline should use classical text classification:

```text
TF-IDF + Logistic Regression
```

Alternative baseline:

```text
TF-IDF + Linear SVM
```

Rationale:

- a binary target is easier to evaluate for the first project-owned model;
- classical models are fast, cheap, and auditable;
- dataset quality should be validated before heavier model families are considered;
- deterministic analysis remains authoritative regardless of model performance.

---

## Label Strategy

The preparation pipeline should preserve the research label taxonomy:

```text
benign
spam
phishing
fraud
unknown
```

The first operational baseline should map those labels into:

```text
benign
suspicious
```

Recommended binary mapping:

| Normalized research label | Binary baseline label | Notes |
|---|---|---|
| `benign` | `benign` | Legitimate operational or personal email. |
| `spam` | `suspicious` | Useful as noisy unwanted email, but should be tracked separately in analysis. |
| `phishing` | `suspicious` | Primary positive class target. |
| `fraud` | `suspicious` | Useful for social-engineering overlap. |
| `unknown` | excluded | Include only after manual review. |

The original label and research label must remain available for per-source analysis so spam performance is not confused with phishing performance.

---

## Initial Dataset Mix

The first experiment should not depend on a single corpus.

Recommended initial source roles:

- benign:
  - SpamAssassin `easy_ham` and `hard_ham`;
  - Enron only after a deliberate privacy and cleaning pass.
- suspicious:
  - phishing-specific corpus if a trustworthy Nazario source or equivalent is confirmed;
  - Fraudulent E-mail Corpus for fraud/social-engineering overlap;
  - carefully audited Kaggle samples only if provenance and licensing are acceptable.
- spam/noise analysis:
  - SpamAssassin `spam`;
  - TREC spam corpora if access and usage terms are confirmed.

PhishShield realistic fixtures must remain outside training and should be used only as qualitative holdout checks.

---

## Baseline Feature Sets

### Baseline 1: Text Only

```text
subject + body_text
```

Goal:

- establish a minimal text-only baseline;
- validate that the prepared corpora contain useful signal;
- reduce dependency on parser-derived metadata in the first experiment.

### Baseline 2: Text Plus Lightweight Metadata

```text
subject + body_text + urls + attachment_filenames
```

Goal:

- test whether URL strings and attachment names improve recall for phishing and fraud;
- remain static and safe without binary parsing, network access, or attachment content analysis.

Deferred feature candidates:

- authentication summary;
- selected normalized headers;
- deterministic finding codes;
- attachment content;
- URL resolution output;
- rendered webpage content.

---

## Split Strategy

The first experiment should use:

```text
train
validation
fixture_holdout
```

Rules:

- split only after exact deduplication;
- keep known duplicate or near-duplicate campaigns in the same split;
- preserve class distribution where possible;
- report source distribution for every split;
- keep PhishShield fixtures out of train, validation, and test;
- use PhishShield fixtures as a qualitative holdout to compare model behavior with deterministic expectations.

---

## Evaluation Metrics

The first model should not be evaluated with accuracy alone.

Minimum metrics:

- precision for `suspicious`;
- recall for `suspicious`;
- F1 for `suspicious`;
- confusion matrix;
- false positive rate on benign email;
- false negative rate on phishing/fraud email;
- per-source performance breakdown.

Required reporting slices:

- benign corporate email;
- generic spam/noise;
- phishing;
- fraud/social engineering;
- PhishShield fixture holdout.

---

## Acceptance Criteria For Moving Beyond Planning

Before adding ingestion or training code, the project should have:

- at least one dataset source with acceptable access and usage terms;
- an agreed canonical prepared sample schema;
- an agreed binary baseline label mapping;
- an agreed deduplication approach;
- an agreed train/validation/test split rule;
- defined metrics and reporting slices;
- a decision on where generated datasets will live outside Git.

Before adding a real inference adapter, the project should additionally have:

- a trained baseline model;
- evaluation results that show clear value over trivial baselines;
- documented false positive and false negative behavior;
- a decision on artifact format;
- a packaging plan that does not require users to install an external AI runtime.

---

## Artifact Direction

The first training experiment may use Python-native artifacts such as:

```text
vectorizer.joblib
classifier.joblib
```

This does not mean the final runtime artifact must stay in that format.

Potential later runtime formats:

- embedded scikit-learn artifacts if dependency cost is acceptable;
- ONNX artifacts if portability and runtime isolation become more important;
- another embedded classifier format if it better fits packaging needs.

No artifact format should be finalized before dataset quality and baseline performance are understood.

---

## Non-Goals

This strategy does not implement:

- dataset download scripts;
- dataset parsing scripts;
- training scripts;
- model artifacts;
- model runtime dependencies;
- endpoint changes;
- frontend changes;
- combined deterministic and model scoring.

---

## Next Implementation Step

The first technical ingestion proof of concept is a small SpamAssassin preparation module under `tools/ml_data_preparation/`.

The first reusable command is:

```text
python -m tools.ml_data_preparation.prepare_spamassassin
```

Recommended first candidate:

```text
Apache SpamAssassin Public Corpus
```

Reason:

- it is simple to access;
- it contains ham and spam groups;
- it is useful for validating ingestion, parsing, normalization, and deduplication mechanics before using more sensitive corpora such as Enron.

The next step after the synthetic POC should be a local dry run with this command against a manually downloaded SpamAssassin subset stored outside Git.

The first dry run has been completed with 20 `easy_ham` and 20 `spam` messages. Both subsets processed without failures and produced JSONL outputs outside the repository.

Prepared JSONL outputs should be validated before any training experiment with:

```text
python -m tools.ml_data_preparation.validate_prepared_dataset
```

The first validation dry run has been completed over those prepared JSONL files:

```text
rows: 40
invalid_rows: 0
duplicate_sample_ids: 0
labels: benign=20, suspicious=20
empty_subject: 0
empty_body: 0
urls_found: 94
```

The next practical validation step should use a larger capped SpamAssassin sample before any baseline training script is introduced.

That larger dry run has now been completed. The full local SpamAssassin subset produced 2501 `benign` rows and 501 `suspicious` rows with zero invalid rows and zero duplicate sample IDs after validation.

Because the full subset is imbalanced, the first training baseline should start with a balanced subset before comparing against a full-data run with class weighting.

The first baseline training command is:

```text
python -m tools.ml_training.train_baseline
```

It trains a balanced TF-IDF logistic regression baseline from prepared JSONL inputs and reports validation metrics without writing model artifacts to the repository.

Training metrics can also be written to JSON with:

```text
python -m tools.ml_training.train_baseline --metrics-output path/to/metrics.json
```

The metrics output is intended for experiment comparison and should be written outside the repository with prepared datasets.

---

## Fixture Holdout Evaluation

PhishShield fixture emails should be used only as holdout evidence, not training data.

The fixture holdout command is:

```text
python -m tools.ml_training.evaluate_fixture_holdout
```

It trains a temporary baseline from prepared JSONL inputs, prepares a fixed set of benign and suspicious PhishShield fixtures, and reports per-fixture predictions plus aggregate holdout metrics.

The first fixture holdout is intended to evaluate whether a SpamAssassin-trained ham/spam baseline transfers any useful signal to realistic PhishShield examples. It is not a production phishing-quality benchmark.

### First fixture holdout result

The first fixture holdout used the SpamAssassin-trained balanced baseline with the `text_with_light_metadata` feature set.

Result:

```text
total: 10
correct: 4
accuracy: 0.4000
false_positive_benign: 5
false_negative_suspicious: 1
```

Per-fixture outcome:

| Fixture | Expected | Predicted | Result |
|---|---|---|---|
| `benign_account_summary.eml` | `benign` | `suspicious` | False positive |
| `benign_invoice_with_pdf.eml` | `benign` | `suspicious` | False positive |
| `benign_security_alert_login_notice.eml` | `benign` | `suspicious` | False positive |
| `benign_html_only_newsletter_notice.eml` | `benign` | `suspicious` | False positive |
| `benign_support_ticket_update.eml` | `benign` | `suspicious` | False positive |
| `suspicious_html_notice.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_shortener_login_notice.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_html_only_credential_lure.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_qr_login_lure.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_cloud_share_auth_failure.eml` | `suspicious` | `benign` | False negative |

Interpretation:

- the SpamAssassin-only baseline validates the mechanics of the ML pipeline;
- it is not acceptable as a phishing model;
- it over-flags benign business/security/support fixtures;
- it misses at least one strong suspicious fixture;
- phishing-specific and benign business-email datasets are required before model artifacts or inference adapters should be considered.

This result blocks model artifact work until the training dataset is expanded beyond SpamAssassin ham/spam.

---

## First Baseline Training Result

The first baseline training run used the prepared SpamAssassin JSONL outputs stored outside the repository:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\spamassassin\prepared\easy_ham_full.jsonl
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\spamassassin\prepared\spam_full.jsonl
```

Common settings:

```text
strategy: balanced
validation_ratio: 0.2
random_seed: 42
samples: 1002
train_samples: 801
validation_samples: 201
labels: benign=501, suspicious=501
```

### Text-only baseline

Feature set:

```text
subject + body_text
```

Result:

```text
accuracy: 0.9701
precision_suspicious: 0.9896
recall_suspicious: 0.9500
f1_suspicious: 0.9694
confusion_matrix_labels: benign,suspicious
confusion_matrix: [[100, 1], [5, 95]]
```

### Text plus lightweight metadata baseline

Feature set:

```text
subject + body_text + urls + attachment_filenames
```

Result:

```text
accuracy: 0.9801
precision_suspicious: 0.9898
recall_suspicious: 0.9700
f1_suspicious: 0.9798
confusion_matrix_labels: benign,suspicious
confusion_matrix: [[100, 1], [3, 97]]
```

### Interpretation

The lightweight metadata feature set improved suspicious recall and F1 on this SpamAssassin ham/spam baseline.

These results validate that the prepared-data to training-metrics pipeline works, but they do not prove phishing detection quality because SpamAssassin is a ham/spam corpus rather than a phishing-specific benchmark.

No model artifacts were written to the repository.

---

## First Metrics JSON Output Result

The first metrics JSON dry run used the same prepared SpamAssassin JSONL files as the first baseline training run:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\spamassassin\prepared\easy_ham_full.jsonl
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\spamassassin\prepared\spam_full.jsonl
```

Metrics were written outside the repository under:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\spamassassin\metrics
```

Generated files:

- `baseline_text.json`
- `baseline_text_metadata.json`

### Text-only metrics JSON

```text
feature_set: text
samples: 1002
train_samples: 801
validation_samples: 201
labels: benign=501, suspicious=501
accuracy: 0.9701492537
precision_suspicious: 0.9895833333
recall_suspicious: 0.9500
f1_suspicious: 0.9693877551
confusion_matrix: [[100, 1], [5, 95]]
```

### Text plus lightweight metadata metrics JSON

```text
feature_set: text_with_light_metadata
samples: 1002
train_samples: 801
validation_samples: 201
labels: benign=501, suspicious=501
accuracy: 0.9800995025
precision_suspicious: 0.9897959184
recall_suspicious: 0.9700
f1_suspicious: 0.9797979798
confusion_matrix: [[100, 1], [3, 97]]
```

The metrics JSON output confirms that baseline runs can now be compared without copying terminal output manually and without writing model artifacts to the repository.
