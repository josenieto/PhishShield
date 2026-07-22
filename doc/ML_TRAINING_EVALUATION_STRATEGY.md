# ML Training And Evaluation Strategy

## Purpose

This document defines the first training and evaluation strategy for a future PhishShield-owned email classification model.

It builds on:

- `doc/ML_DATASET_RESEARCH.md`
- `doc/ML_DATA_PREPARATION_PLAN.md`
- `doc/MODEL_ASSISTED_ANALYSIS_PLAN.md`

This document does not introduce training scripts, model artifacts, runtime dependencies, or inference adapters.

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

Recommended first candidate:

```text
Apache SpamAssassin Public Corpus
```

Reason:

- it is simple to access;
- it contains ham and spam groups;
- it is useful for validating ingestion, parsing, normalization, and deduplication mechanics before using more sensitive corpora such as Enron.

The next step after the synthetic POC should be a local dry run against a manually downloaded SpamAssassin subset stored outside Git.
