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

### Next dataset candidate

The next candidate to investigate is the Fraudulent E-mail Corpus.

This follows from the fixture holdout result: the current SpamAssassin-trained baseline exercises the training and evaluation tooling, but it does not model phishing or benign business-email behavior well enough for artifact work.

The next step is limited to dataset research:

- verify access and source stability;
- record license and redistribution constraints;
- inspect raw message format and labels;
- review PII and sensitive-content handling needs;
- decide whether a focused ingestion prototype is justified.

The Fraudulent E-mail Corpus is expected to add fraud and social-engineering language coverage. It is not expected to fully replace a modern credential-phishing corpus, so Nazario or another trustworthy phishing-specific source should remain a later target if access and licensing can be confirmed.

Preparation tooling for this corpus should be developed with synthetic tests only. The real corpus should be processed in Kaggle or another isolated environment, and generated JSONL outputs should remain outside the repository.

A Kaggle structural inspection found `3906` detected messages, `3839` subjects, `52` empty bodies, and `2781` body URLs. A naive whole-file UTF-8 decode produced `10524` replacement characters, so preparation should preserve raw bytes and let the email parser handle per-message charset and MIME decoding.

A follow-up Kaggle preparation test with non-standard charset fallback processed all `3906` detected messages with `0` failures, `0` invalid rows, `0` duplicate sample IDs, `88` empty subjects, `85` empty bodies, and `2161` extracted URLs. This makes the corpus usable for the next fraud/social-engineering baseline experiment, while keeping raw and generated data outside Git.

### Fraud corpus baseline result

The first fraud/social-engineering baseline used SpamAssassin `easy_ham_full.jsonl` as the benign source and the prepared Fraudulent E-mail Corpus JSONL as the suspicious source.

Input files were stored outside the repository:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\spamassassin\prepared\easy_ham_full.jsonl
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\fraudulent-email-corpus\prepared\fraudulent_email_corpus_charset_fallback.jsonl
```

Prepared Fraudulent E-mail Corpus validation result:

```text
files: 1
rows: 3906
invalid_rows: 0
duplicate_sample_ids: 0
labels: suspicious=3906
empty_subject: 88
empty_body: 85
urls_found: 2161
```

Training settings:

```text
strategy: balanced
feature_set: text_with_light_metadata
validation_ratio: 0.2
random_seed: 42
samples: 5002
train_samples: 4001
validation_samples: 1001
labels: benign=2501, suspicious=2501
```

Validation result:

```text
accuracy: 0.9860
precision_suspicious: 1.0000
recall_suspicious: 0.9720
f1_suspicious: 0.9858
confusion_matrix_labels: benign,suspicious
confusion_matrix: [[501, 0], [14, 486]]
```

PhishShield fixture holdout result:

```text
total: 10
correct: 4
accuracy: 0.4000
false_positive_benign: 1
false_negative_suspicious: 5
```

Per-fixture outcome:

| Fixture | Expected | Predicted | Result |
|---|---|---|---|
| `benign_account_summary.eml` | `benign` | `benign` | Correct |
| `benign_invoice_with_pdf.eml` | `benign` | `suspicious` | False positive |
| `benign_security_alert_login_notice.eml` | `benign` | `benign` | Correct |
| `benign_html_only_newsletter_notice.eml` | `benign` | `benign` | Correct |
| `benign_support_ticket_update.eml` | `benign` | `benign` | Correct |
| `suspicious_html_notice.eml` | `suspicious` | `benign` | False negative |
| `suspicious_shortener_login_notice.eml` | `suspicious` | `benign` | False negative |
| `suspicious_html_only_credential_lure.eml` | `suspicious` | `benign` | False negative |
| `suspicious_qr_login_lure.eml` | `suspicious` | `benign` | False negative |
| `suspicious_cloud_share_auth_failure.eml` | `suspicious` | `benign` | False negative |

Comparison with the SpamAssassin-only holdout:

```text
SpamAssassin-only: accuracy=0.4000, false_positive_benign=5, false_negative_suspicious=1
Fraud corpus baseline: accuracy=0.4000, false_positive_benign=1, false_negative_suspicious=5
```

Interpretation:

- the Fraudulent E-mail Corpus improves benign fixture behavior by reducing false positives;
- it does not improve phishing fixture recall and misses all suspicious holdout fixtures;
- validation metrics inside the training sources remain high, but the fixture holdout confirms that 419 fraud language is not enough for modern phishing behavior;
- model artifact and inference adapter work remain blocked until modern phishing-specific data is added.

### Next modern phishing dataset candidate

The next selected candidate is `Phishing Email Detection`:

```text
Kaggle: https://www.kaggle.com/datasets/subhajournal/phishingemails
Hugging Face mirror: https://huggingface.co/datasets/zefang-liu/phishing-email-dataset
```

Observed metadata:

```text
license: LGPL-3.0
format: CSV
rows: approximately 18.7k in the Hugging Face mirror
columns: Email Text, Email Type
labels: Safe Email, Phishing Email
```

Reason for selecting it:

- it contains labeled email text rather than only phishing URLs;
- it is more directly aligned with phishing email classification than SpamAssassin spam or 419 fraud;
- it has enough rows for a controlled baseline experiment;
- it is smaller and simpler than mixed URL/email or aggregated benchmark corpora.

Required verification before training:

- confirm downloaded schema and label values;
- inspect null, empty, duplicate, and URL-only rows;
- map labels into `benign` and `suspicious` consistently;
- keep generated JSONL outside Git;
- evaluate against the same PhishShield fixture holdout before any model artifact decision.

Schema and quality verification result:

```text
bytes: 52034604
columns: '', Email Text, Email Type
rows: 18650
parse_errors: 0
labels: Safe Email=11322, Phishing Email=7328
empty_text: 19
duplicate_text: 1127
duplicate_text_ratio: 0.0604
short_rows_lt_30: 584
long_rows_gt_10000: 397
url_only_rows: 1
```

Decision:

- approve a controlled preparation POC;
- require quality counters and cleaning for empty, duplicate, short, long, URL-only, and spam-like rows;
- do not treat the source as a clean modern phishing corpus;
- keep model artifact and inference adapter work deferred until fixture holdout improves.

Preparation POC result:

```text
rows_read: 18650
processed: 18631
failed: 0
skipped_empty_text: 19
unsupported_label: 0
duplicate_text: 1109
short_rows_lt_30: 584
long_rows_gt_10000: 397
url_only_rows: 1
no_alpha_rows: 1
urls_found: 13291
labels: benign=11322, suspicious=7309
```

Prepared JSONL validation result:

```text
rows: 18631
invalid_rows: 0
duplicate_sample_ids: 0
labels: benign=11322, suspicious=7309
empty_subject: 18631
empty_body: 0
urls_found: 13291
```

The next experiment should train a baseline from this prepared JSONL and evaluate the same PhishShield fixture holdout before deciding whether this noisy phishing/spam text source improves suspicious recall.

### Phishing Email Detection baseline result

The first `Phishing Email Detection` baseline used only the prepared JSONL from this dataset because it already contains both `benign` and `suspicious` labels.

Input file stored outside the repository:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\phishing-email-detection\prepared\phishing_email_detection.jsonl
```

Training settings:

```text
strategy: balanced
feature_set: text_with_light_metadata
validation_ratio: 0.2
random_seed: 42
samples: 14618
train_samples: 11694
validation_samples: 2924
labels: benign=7309, suspicious=7309
```

Validation result:

```text
accuracy: 0.9661
precision_suspicious: 0.9522
recall_suspicious: 0.9815
f1_suspicious: 0.9667
confusion_matrix_labels: benign,suspicious
confusion_matrix: [[1390, 72], [27, 1435]]
```

PhishShield fixture holdout result:

```text
total: 10
correct: 7
accuracy: 0.7000
false_positive_benign: 3
false_negative_suspicious: 0
```

Per-fixture outcome:

| Fixture | Expected | Predicted | Result |
|---|---|---|---|
| `benign_account_summary.eml` | `benign` | `suspicious` | False positive |
| `benign_invoice_with_pdf.eml` | `benign` | `benign` | Correct |
| `benign_security_alert_login_notice.eml` | `benign` | `suspicious` | False positive |
| `benign_html_only_newsletter_notice.eml` | `benign` | `suspicious` | False positive |
| `benign_support_ticket_update.eml` | `benign` | `benign` | Correct |
| `suspicious_html_notice.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_shortener_login_notice.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_html_only_credential_lure.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_qr_login_lure.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_cloud_share_auth_failure.eml` | `suspicious` | `suspicious` | Correct |

Comparison with previous fixture holdouts:

```text
SpamAssassin-only: accuracy=0.4000, false_positive_benign=5, false_negative_suspicious=1
Fraud corpus baseline: accuracy=0.4000, false_positive_benign=1, false_negative_suspicious=5
Phishing Email Detection baseline: accuracy=0.7000, false_positive_benign=3, false_negative_suspicious=0
```

Interpretation:

- this is the first baseline that improves PhishShield fixture holdout accuracy;
- it eliminates suspicious fixture false negatives in the current 10-fixture holdout;
- it still over-flags three benign fixtures, so benign business-email quality remains a concern;
- model artifact and inference adapter work remain deferred until additional validation, calibration, and a larger holdout strategy are in place.

### Expanded fixture holdout result

The fixture holdout was expanded from 10 to 16 examples by adding account, MFA, newsletter, QR invoice, and cloud storage cases.

Added benign fixtures:

```text
benign_account_usage_digest.eml
benign_mfa_enabled_notice.eml
benign_html_product_newsletter_account_preferences.eml
```

Added suspicious fixtures:

```text
suspicious_mfa_push_approval_lure.eml
suspicious_shared_invoice_qr_lure.eml
suspicious_cloud_storage_quota_lure.eml
```

Expanded holdout result for the `Phishing Email Detection` baseline:

```text
total: 16
correct: 10
accuracy: 0.6250
false_positive_benign: 6
false_negative_suspicious: 0
```

Per-fixture outcome:

| Fixture | Expected | Predicted | Result |
|---|---|---|---|
| `benign_account_summary.eml` | `benign` | `suspicious` | False positive |
| `benign_account_usage_digest.eml` | `benign` | `suspicious` | False positive |
| `benign_invoice_with_pdf.eml` | `benign` | `benign` | Correct |
| `benign_security_alert_login_notice.eml` | `benign` | `suspicious` | False positive |
| `benign_mfa_enabled_notice.eml` | `benign` | `suspicious` | False positive |
| `benign_html_only_newsletter_notice.eml` | `benign` | `suspicious` | False positive |
| `benign_html_product_newsletter_account_preferences.eml` | `benign` | `suspicious` | False positive |
| `benign_support_ticket_update.eml` | `benign` | `benign` | Correct |
| `suspicious_html_notice.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_shortener_login_notice.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_html_only_credential_lure.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_qr_login_lure.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_cloud_share_auth_failure.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_mfa_push_approval_lure.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_shared_invoice_qr_lure.eml` | `suspicious` | `suspicious` | Correct |
| `suspicious_cloud_storage_quota_lure.eml` | `suspicious` | `suspicious` | Correct |

Expanded holdout interpretation:

- suspicious fixture recall remains strong with zero false negatives;
- benign false positives increased from `3` of `5` benign fixtures to `6` of `8` benign fixtures;
- benign account, MFA/security, and newsletter-style messages are the main calibration gap;
- model artifact and inference adapter work remain blocked until benign calibration improves.

### Threshold sweep result

The holdout evaluator was extended to support an optional suspicious probability threshold so the phishing baseline could be checked for a simple calibration improvement.

Threshold sweep against the expanded 16-fixture holdout:

| Suspicious threshold | Accuracy | False positive benign | False negative suspicious |
|---:|---:|---:|---:|
| `0.50` | `0.6250` | `6` | `0` |
| `0.55` | `0.5625` | `6` | `1` |
| `0.60` | `0.5625` | `6` | `1` |
| `0.65` | `0.5625` | `6` | `1` |
| `0.70` | `0.3750` | `6` | `4` |
| `0.75` | `0.3125` | `6` | `5` |
| `0.80` | `0.3125` | `5` | `6` |
| `0.85` | `0.3750` | `3` | `7` |
| `0.90` | `0.5000` | `0` | `8` |

Per-fixture suspicious probabilities at threshold `0.50` showed strong overlap between benign account/security/newsletter fixtures and suspicious fixtures. Examples:

```text
benign_account_usage_digest.eml: 0.8943
benign_mfa_enabled_notice.eml: 0.8989
benign_security_alert_login_notice.eml: 0.8473
suspicious_mfa_push_approval_lure.eml: 0.5468
suspicious_qr_login_lure.eml: 0.6585
suspicious_cloud_storage_quota_lure.eml: 0.6938
```

Interpretation:

- thresholding alone does not improve the expanded holdout;
- several benign fixtures score more suspicious than weaker suspicious fixtures;
- the next ML issue is training data/calibration quality, not a simple decision threshold;
- model artifact and inference adapter work remain blocked.

### Next benign calibration source

The next selected benign calibration source is SpamAssassin `hard_ham`.

Reason:

- the expanded holdout failure mode is false positives on benign account, MFA/security, and newsletter-like messages;
- thresholding alone did not improve the holdout;
- `hard_ham` is the lowest-friction source of more difficult benign email examples because the project already has SpamAssassin preparation tooling;
- Enron is likely more business-realistic, but it has higher privacy, cleanup, deduplication, and source-integrity risk.

Planned experiment:

```text
benign: Phishing Email Detection benign rows + SpamAssassin hard_ham rows
suspicious: Phishing Email Detection suspicious rows
feature_set: text_with_light_metadata
strategy: balanced
random_seed: 42
evaluation: expanded PhishShield fixture holdout
```

Success criteria:

```text
false_positive_benign < 6
false_negative_suspicious <= 1
accuracy > 0.6250
```

If `hard_ham` does not improve benign calibration, the next research target should be Enron or another business-email source with explicit PII and cleanup controls.

### Hard ham calibration result

Three calibration variants were evaluated against the expanded PhishShield fixture holdout:

```text
baseline: Phishing Email Detection only
A: Phishing Email Detection + hard_ham_20021010
B: Phishing Email Detection + hard_ham_20030228
C: Phishing Email Detection + both hard_ham subsets
```

Training validation metrics:

| Variant | Accuracy | Precision suspicious | Recall suspicious | F1 suspicious | Confusion matrix |
|---|---:|---:|---:|---:|---|
| Baseline | `0.9661` | `0.9522` | `0.9815` | `0.9667` | `[[1390, 72], [27, 1435]]` |
| A | `0.9658` | `0.9540` | `0.9788` | `0.9662` | `[[1393, 69], [31, 1431]]` |
| B | `0.9682` | `0.9585` | `0.9788` | `0.9685` | `[[1400, 62], [31, 1431]]` |
| C | `0.9679` | `0.9572` | `0.9795` | `0.9682` | `[[1398, 64], [30, 1432]]` |

Expanded holdout metrics:

| Variant | Accuracy | False positive benign | False negative suspicious |
|---|---:|---:|---:|
| Baseline | `0.6250` | `6` | `0` |
| A | `0.6250` | `6` | `0` |
| B | `0.6250` | `6` | `0` |
| C | `0.6250` | `6` | `0` |

Interpretation:

- adding SpamAssassin `hard_ham` does not improve the expanded holdout;
- validation metrics move slightly, but fixture behavior is unchanged;
- `hard_ham` is not sufficient for benign account, MFA/security, and newsletter calibration;
- the next benign source should be Enron or another business-email corpus with explicit privacy and cleanup controls.

### Enron benign calibration plan

The next benign calibration workflow candidate is the Enron Email Dataset.

Reference:

```text
https://www.cs.cmu.edu/~enron/
https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz
```

Reason:

- SpamAssassin `hard_ham` did not change expanded holdout behavior;
- false positives are concentrated in benign account, MFA/security, and newsletter-like messages;
- Enron provides realistic business-email language, which is closer to the false-positive class than SpamAssassin ham.

Constraints before ingestion:

- plan privacy and PII handling;
- keep raw and prepared Enron data outside Git;
- use synthetic unit tests only;
- report aggregate metrics only;
- start with a capped preparation POC;
- track mailbox/folder distribution to avoid source leakage;
- do not use mailbox owner, folder path, or source metadata as model text features.

Planned first Enron calibration experiment:

```text
benign: Phishing Email Detection benign rows + capped Enron benign rows
suspicious: Phishing Email Detection suspicious rows
feature_set: text_with_light_metadata
strategy: balanced
evaluation: expanded PhishShield fixture holdout
```

Success criteria remain:

```text
false_positive_benign < 6
false_negative_suspicious <= 1
accuracy > 0.6250
```

Model artifact and inference adapter work remain blocked until the expanded holdout improves and the data-handling risks are addressed.

### Enron capped POC result

The first Enron POC used a capped `1000` message sample from the extracted `maildir` directory and combined it with the prepared `Phishing Email Detection` JSONL.

Prepared Enron validation result:

```text
rows: 1000
invalid_rows: 0
duplicate_sample_ids: 0
labels: benign=1000
empty_subject: 196
empty_body: 0
urls_found: 703
```

Training validation metrics:

```text
samples: 14618
train_samples: 11694
validation_samples: 2924
labels: benign=7309, suspicious=7309
accuracy: 0.9634
precision_suspicious: 0.9520
recall_suspicious: 0.9761
f1_suspicious: 0.9639
confusion_matrix: [[1390, 72], [35, 1427]]
```

Expanded holdout result:

```text
total: 16
correct: 9
accuracy: 0.5625
false_positive_benign: 6
false_negative_suspicious: 1
```

Comparison:

```text
Phishing Email Detection baseline: accuracy=0.6250, false_positive_benign=6, false_negative_suspicious=0
Phishing Email Detection + Enron 1000: accuracy=0.5625, false_positive_benign=6, false_negative_suspicious=1
```

Interpretation:

- the first capped Enron sample validates preparation mechanics but does not improve benign calibration;
- the sample is source-narrow (`users_seen=1`), so it should not be treated as a representative Enron calibration result;
- adding this sample introduced one suspicious false negative without reducing benign false positives;
- the next Enron experiment should sample across multiple users/folders or deliberately target benign account/security/newsletter-like folders before drawing stronger conclusions.

### Enron source-diverse POC result

The second Enron POC used the same extracted `maildir` directory but applied source-diverse caps:

```text
limit: 2000
max_per_user: 50
max_per_folder: 20
```

Prepared Enron validation result:

```text
rows: 2000
invalid_rows: 0
duplicate_sample_ids: 0
labels: benign=2000
empty_subject: 55
empty_body: 0
urls_found: 1472
users_seen: 58
folders_seen: 244
```

Training validation metrics:

```text
samples: 14618
train_samples: 11694
validation_samples: 2924
labels: benign=7309, suspicious=7309
accuracy: 0.9651
precision_suspicious: 0.9474
recall_suspicious: 0.9850
f1_suspicious: 0.9658
confusion_matrix: [[1382, 80], [22, 1440]]
```

Expanded holdout result:

```text
total: 16
correct: 10
accuracy: 0.6250
false_positive_benign: 6
false_negative_suspicious: 0
```

Comparison:

```text
Phishing Email Detection baseline: accuracy=0.6250, false_positive_benign=6, false_negative_suspicious=0
Phishing Email Detection + Enron 1000: accuracy=0.5625, false_positive_benign=6, false_negative_suspicious=1
Phishing Email Detection + Enron diverse 2000: accuracy=0.6250, false_positive_benign=6, false_negative_suspicious=0
```

Interpretation:

- source-diverse Enron sampling improves over the first narrow Enron sample, but only returns to the original `Phishing Email Detection` baseline;
- Enron does not reduce benign false positives on the expanded holdout in this configuration;
- the persistent false positives are still account, MFA/security, and newsletter-style fixtures;
- the next calibration direction should target notification-like benign data or introduce feature/source-aware calibration rather than adding generic business email alone.

### Synthetic benign notification calibration result

Synthetic benign notification templates were generated for account, MFA/security, newsletter, cloud-share, billing, support, HR, and vendor notification families.

The first generated dataset used `10` samples per category:

```text
rows: 120
labels: benign=120
urls_found: 120
```

Training validation metrics with `Phishing Email Detection + synthetic benign notifications 120`:

```text
samples: 14618
train_samples: 11694
validation_samples: 2924
labels: benign=7309, suspicious=7309
accuracy: 0.9651
precision_suspicious: 0.9552
recall_suspicious: 0.9761
f1_suspicious: 0.9655
confusion_matrix: [[1395, 67], [35, 1427]]
```

Expanded holdout result:

```text
total: 16
correct: 10
accuracy: 0.6250
false_positive_benign: 2
false_negative_suspicious: 4
```

A larger generated dataset used `50` samples per category:

```text
rows: 600
labels: benign=600
urls_found: 600
```

Training validation metrics with `Phishing Email Detection + synthetic benign notifications 600`:

```text
samples: 14618
train_samples: 11694
validation_samples: 2924
labels: benign=7309, suspicious=7309
accuracy: 0.9655
precision_suspicious: 0.9510
recall_suspicious: 0.9815
f1_suspicious: 0.9660
confusion_matrix: [[1388, 74], [27, 1435]]
```

Expanded holdout result:

```text
total: 16
correct: 9
accuracy: 0.5625
false_positive_benign: 1
false_negative_suspicious: 6
```

Comparison:

```text
Phishing Email Detection baseline: accuracy=0.6250, false_positive_benign=6, false_negative_suspicious=0
Synthetic benign notifications 120: accuracy=0.6250, false_positive_benign=2, false_negative_suspicious=4
Synthetic benign notifications 600: accuracy=0.5625, false_positive_benign=1, false_negative_suspicious=6
```

Interpretation:

- synthetic benign notification data directly reduces the targeted benign false positives;
- increasing synthetic benign volume over-calibrates toward benign and creates too many suspicious false negatives;
- the useful next direction is not simply adding more synthetic benign data, but balancing synthetic benign notifications with additional suspicious notification-style lures or source-aware calibration;
- model artifact and inference adapter work remain blocked.

### Synthetic balanced notification calibration result

Synthetic suspicious notification-style lures were added to balance the synthetic benign notification calibration set.

Evaluated variants:

```text
A: Phishing Email Detection + synthetic benign 120 + synthetic suspicious 120
B: Phishing Email Detection + synthetic benign 600 + synthetic suspicious 600
C: Phishing Email Detection + synthetic benign 120 + synthetic suspicious 240
```

Training validation metrics:

| Variant | Accuracy | Precision suspicious | Recall suspicious | F1 suspicious | Confusion matrix |
|---|---:|---:|---:|---:|---|
| A 120/120 | `0.9680` | `0.9549` | `0.9825` | `0.9685` | `[[1417, 69], [26, 1460]]` |
| B 600/600 | `0.9681` | `0.9535` | `0.9842` | `0.9686` | `[[1506, 76], [25, 1557]]` |
| C 120/240 | `0.9652` | `0.9524` | `0.9795` | `0.9657` | `[[1436, 74], [31, 1479]]` |

Expanded holdout metrics:

| Variant | Accuracy | False positive benign | False negative suspicious |
|---|---:|---:|---:|
| Baseline | `0.6250` | `6` | `0` |
| Synthetic benign 120 | `0.6250` | `2` | `4` |
| Synthetic benign 600 | `0.5625` | `1` | `6` |
| A 120/120 | `0.5625` | `6` | `1` |
| B 600/600 | `0.8125` | `2` | `1` |
| C 120/240 | `0.6250` | `6` | `0` |

Interpretation:

- balanced synthetic notification calibration is the first variant that improves both accuracy and benign false positives while keeping suspicious false negatives low;
- variant B meets the current success criteria with `accuracy=0.8125`, `false_positive_benign=2`, and `false_negative_suspicious=1`;
- variant A over-emphasizes suspicious notification lures relative to benign coverage and reintroduces benign false positives;
- variant C behaves like the original baseline on the expanded holdout;
- model artifact and inference adapter work remain deferred until this calibration approach is validated on a larger holdout and with non-synthetic benign notification data.

### 32-fixture notification holdout result

The holdout was expanded from 16 to 32 fixtures to stress whether synthetic notification calibration generalizes beyond the first fixture set.

Added benign fixtures:

```text
benign_account_billing_summary.eml
benign_device_login_history.eml
benign_mfa_recovery_codes_notice.eml
benign_newsletter_security_tips.eml
benign_cloud_storage_usage_digest.eml
benign_vendor_invoice_status_update.eml
benign_hr_benefits_reminder.eml
benign_support_case_waiting_customer.eml
```

Added suspicious fixtures:

```text
suspicious_device_login_verification_lure.eml
suspicious_mfa_recovery_codes_lure.eml
suspicious_billing_profile_reauth_lure.eml
suspicious_cloud_storage_expiry_lure.eml
suspicious_vendor_invoice_portal_lure.eml
suspicious_hr_benefits_login_lure.eml
suspicious_support_case_auth_lure.eml
suspicious_newsletter_preferences_credential_lure.eml
```

32-fixture comparison:

| Variant | Accuracy | False positive benign | False negative suspicious |
|---|---:|---:|---:|
| Baseline | `0.6250` | `11` | `1` |
| Variant B 600/600 | `0.8750` | `3` | `1` |

Baseline 32-fixture result:

```text
total: 32
correct: 20
accuracy: 0.6250
false_positive_benign: 11
false_negative_suspicious: 1
```

Variant B 32-fixture result:

```text
total: 32
correct: 28
accuracy: 0.8750
false_positive_benign: 3
false_negative_suspicious: 1
```

Interpretation:

- Variant B remains the strongest current calibration direction on the larger holdout;
- the balanced synthetic notification calibration reduced benign false positives from `11` to `3` without increasing suspicious false negatives;
- remaining benign false positives are still concentrated around account, MFA recovery, and newsletter-like language;
- model artifact and inference adapter work remain deferred until the holdout expands further and a non-synthetic validation source confirms the calibration behavior.

### Baseline selection phase conclusion

The current experimental ML baseline candidate is:

```text
TF-IDF + Logistic Regression
training data: Phishing Email Detection + synthetic benign notifications 600 + synthetic suspicious notifications 600
feature_set: text_with_light_metadata
```

Selection evidence:

```text
expanded holdout size: 32 fixtures
accuracy: 0.8750
false_positive_benign: 3
false_negative_suspicious: 1
```

Experiment summary:

| Experiment | Holdout size | Accuracy | False positive benign | False negative suspicious | Decision |
|---|---:|---:|---:|---:|---|
| SpamAssassin-only baseline | `10` | `0.4000` | `5` | `1` | Reject |
| Fraudulent E-mail Corpus baseline | `10` | `0.4000` | `1` | `5` | Reject |
| Phishing Email Detection baseline | `16` | `0.6250` | `6` | `0` | Partial |
| Threshold sweep | `16` | no improvement | - | - | Reject |
| SpamAssassin `hard_ham` calibration | `16` | `0.6250` | `6` | `0` | Reject |
| Enron capped sample | `16` | `0.5625` | `6` | `1` | Reject |
| Enron source-diverse sample | `16` | `0.6250` | `6` | `0` | Defer |
| Synthetic benign notifications `120` | `16` | `0.6250` | `2` | `4` | Partial |
| Synthetic benign notifications `600` | `16` | `0.5625` | `1` | `6` | Reject |
| Balanced synthetic notifications A `120/120` | `16` | `0.5625` | `6` | `1` | Reject |
| Balanced synthetic notifications B `600/600` | `16` | `0.8125` | `2` | `1` | Promising |
| Balanced synthetic notifications C `120/240` | `16` | `0.6250` | `6` | `0` | Reject |
| Phishing Email Detection baseline | `32` | `0.6250` | `11` | `1` | Baseline |
| Balanced synthetic notifications B `600/600` | `32` | `0.8750` | `3` | `1` | Candidate |

Decision:

- close the baseline selection phase with Variant B as the current experimental candidate;
- keep generated datasets and metrics outside Git;
- do not export or wire a production model artifact yet;
- require at least one more non-synthetic notification-style validation source or a larger independent holdout before treating the candidate as product-ready.

Next ML phase:

- define an experimental artifact export contract outside Git;
- add model-card metadata for the selected candidate;
- validate against additional non-synthetic notification-like benign and suspicious examples;
- keep deterministic analysis authoritative even if a model-assisted path is later enabled.

### Experimental artifact export result

The selected experimental baseline candidate was exported outside Git as a scikit-learn `joblib` artifact with metadata.

Export command:

```text
python -m tools.ml_training.export_baseline_artifact --input "C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\phishing-email-detection\prepared\phishing_email_detection.jsonl" --input "C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\synthetic-benign-notifications\prepared\synthetic_benign_notifications_600.jsonl" --input "C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\synthetic-suspicious-notifications\prepared\synthetic_suspicious_notifications_600.jsonl" --feature-set text_with_light_metadata --strategy balanced --random-seed 42 --model-output "C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\models\phishshield_baseline_candidate.joblib" --metadata-output "C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\models\phishshield_baseline_candidate.metadata.json" --holdout-accuracy 0.875 --holdout-false-positive-benign 3 --holdout-false-negative-suspicious 1
```

Output files:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\models\phishshield_baseline_candidate.joblib
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\models\phishshield_baseline_candidate.metadata.json
```

Exported training metrics:

```text
samples: 15818
train_samples: 12654
validation_samples: 3164
labels: benign=7909, suspicious=7909
accuracy: 0.9681
precision_suspicious: 0.9535
recall_suspicious: 0.9842
f1_suspicious: 0.9686
```

Metadata summary:

```text
model_name: phishshield_baseline_candidate
model_type: tfidf_logistic_regression
status: experimental
feature_set: text_with_light_metadata
holdout_reference: PhishShield 32-fixture notification holdout, accuracy=0.8750, false_positive_benign=3, false_negative_suspicious=1
```

Decision:

- the artifact is exported only for experimental follow-up work;
- the artifact and metadata stay outside Git;
- no runtime inference adapter is enabled by this step;
- deterministic analysis remains authoritative;
- product-facing model-assisted inference remains deferred.

Secondary candidates:

- `cybersectony/PhishingEmailDetectionv2.0`: large mixed email/URL dataset; use only after isolating email rows and clarifying license.
- `it4lia/PhishingEmailCuratedDatasets_Cleaned`: large cleaned aggregation; defer until source overlap, leakage, and benchmark split controls are designed.

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
