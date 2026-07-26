# ML Data Preparation Plan

## Purpose

This document defines how public email corpora should be converted into clean, auditable, and reproducible datasets for future PhishShield model training and evaluation.

It builds on `doc/ML_DATASET_RESEARCH.md` and focuses on preparation rules, not training implementation.

This document does not introduce scripts, dependencies, model artifacts, or inference runtime changes.

---

## Preparation Goals

The data preparation pipeline should:

- normalize heterogeneous public email sources into one canonical sample shape;
- preserve enough source metadata to audit provenance and label mapping;
- reduce duplicate and near-duplicate leakage across train, validation, and test sets;
- protect privacy and avoid committing raw corpora to the repository;
- keep PhishShield fixtures as holdout evidence rather than training data;
- support simple baseline models before heavier model families are considered.

---

## Tooling Location

Dataset preparation tooling lives under:

```text
tools/ml_data_preparation/
```

This tooling is not part of the runtime application layers. It may reuse stable parser adapters from `src/infrastructure/` when that avoids duplicating `.eml` parsing behavior, but runtime application code must not depend on tooling modules.

Generated datasets, downloaded corpora, and intermediate preparation outputs must stay outside the Git repository unless a future decision explicitly allows a small, sanitized fixture.

The first implemented tooling command is:

```text
python -m tools.ml_data_preparation.prepare_spamassassin
```

It prepares a local SpamAssassin email directory into JSONL and does not download corpora or train models.

Prepared JSONL outputs can be validated with:

```text
python -m tools.ml_data_preparation.validate_prepared_dataset
```

---

## Canonical Email Sample Schema

Every prepared sample should be normalized to a shape conceptually equivalent to:

```json
{
  "sample_id": "sha256-of-normalized-core-fields",
  "source": "spamassassin",
  "source_id": "original-message-or-file-id",
  "source_uri": "https://example.org/dataset",
  "original_label": "easy_ham",
  "normalized_label": "benign",
  "subject": "...",
  "body_text": "...",
  "sender_domain": "example.com",
  "urls": ["https://example.com/login"],
  "attachment_filenames": ["invoice.pdf"],
  "raw_available": true,
  "metadata": {
    "license_notes": "...",
    "split_group": "..."
  }
}
```

The schema is intentionally independent from the current API response model. It is a training/evaluation data shape, not a runtime API contract.

---

## Label Taxonomy

The preparation pipeline should preserve two labels:

- `original_label`: the label from the source dataset;
- `normalized_label`: the PhishShield-normalized label.

Recommended normalized labels for research:

```text
benign
spam
phishing
fraud
unknown
```

Recommended first operational baseline mapping:

```text
benign -> benign
spam -> suspicious
phishing -> suspicious
fraud -> suspicious
unknown -> excluded unless manually reviewed
```

Rationale:

- multi-class labels are useful for research and error analysis;
- a binary baseline is simpler for the first model;
- preserving the original label prevents losing important dataset semantics.

---

## Ingestion Rules

Each dataset ingestion definition should record:

- source name;
- source URL;
- download or access instructions;
- license notes;
- raw format;
- original labels;
- normalized label mapping;
- parsing strategy;
- exclusion criteria.

Examples of exclusion criteria:

- unclear license;
- missing message body;
- corrupted message that cannot be parsed safely;
- duplicate of a sample already assigned to another split;
- sample contains labels embedded in its visible content or filename.

---

## Normalization Rules

The first preparation pipeline should normalize each email with deterministic, reproducible steps:

1. Parse the source email or dataset row into subject and body fields.
2. Decode MIME, quoted-printable, base64, and declared charsets where possible.
3. Convert HTML bodies to visible text for text-based features.
4. Extract visible HTTP/HTTPS URLs and HTML anchor `href` URLs when available.
5. Normalize Unicode to a consistent representation.
6. Normalize whitespace.
7. Preserve original casing for stored text, but allow lowercasing in feature extraction.
8. Truncate extremely long fields with a documented limit.
9. Ignore binary attachment content for the first baseline.
10. Preserve attachment filenames as metadata text when available.

The initial baseline should not execute scripts, resolve short links, open URLs, parse PDF/Office contents, or inspect binary attachment payloads.

---

## Deduplication Strategy

Deduplication should happen before splitting data.

Recommended first-pass identifiers:

- hash of normalized `subject + body_text`;
- hash of normalized `body_text`;
- optional hash of URL set and attachment filename set.

Rules:

- exact duplicates must not appear across train, validation, and test sets;
- mirrored samples from different corpora should be collapsed or assigned to the same split group;
- repeated campaign templates should be reviewed before random splitting;
- near-duplicate detection can be deferred until exact deduplication is implemented.

---

## Leakage Prevention

The pipeline must prevent the model from learning dataset artifacts instead of phishing behavior.

Do not include these as direct model features in the first baseline:

- dataset filename;
- local file path;
- source dataset name;
- label text;
- collection-specific IDs;
- train/test split metadata.

Review carefully before including:

- raw headers;
- full sender addresses;
- date headers;
- message IDs;
- mailing-list headers.

Leakage checks should include per-source evaluation so the model cannot look good only because train and test samples share source-specific artifacts.

---

## Privacy And PII Handling

Public email datasets can still contain sensitive data.

Rules:

- do not commit raw corpora to the repository;
- do not commit prepared samples containing PII unless there is a documented reason and compatible license;
- prefer reproducible scripts and source documentation over storing derived datasets in Git;
- redact, hash, or omit email addresses and names in any small illustrative samples;
- treat Enron-derived data with extra caution because it contains real corporate communication.

---

## Split Strategy

The first prepared dataset should support:

```text
train
validation
holdout
```

Recommended rules:
- split after deduplication;
- keep near-duplicate campaigns in the same split when detected;
- preserve class distribution where possible;
- track source distribution per split;
- keep PhishShield realistic fixtures out of training;
- use PhishShield fixtures as a qualitative holdout and regression sanity check.

---

## Baseline Feature Sets

Start with simple, auditable feature sets.

### Baseline 1

```text
subject + body_text
```

Purpose:

- establish a low-cost text-only baseline;
- measure whether public corpora have enough useful signal before adding more features.

### Baseline 2

```text
subject + body_text + urls + attachment_filenames
```

Purpose:

- test whether explicit URL and attachment filename text improves phishing/fraud recall;
- still avoid binary parsing or network access.

Deferred feature candidates:

- authentication summary;
- selected normalized headers;
- deterministic finding codes;
- attachment content;
- rendered page content.

---

## Evaluation Metrics

Do not rely on accuracy alone.

Minimum metrics:

- precision;
- recall;
- F1;
- confusion matrix;
- false positive rate on benign email;
- false negative rate on phishing email;
- per-source performance breakdown.

Recommended reporting slices:

- benign corporate email;
- generic spam;
- phishing;
- fraud/social engineering;
- PhishShield fixture holdout.

---

## Non-Goals

This preparation plan does not implement:

- dataset download scripts;
- training scripts;
- model artifacts;
- model runtime dependencies;
- API or frontend changes;
- automatic dataset redistribution.

Implemented preparation commands currently cover:

- SpamAssassin directory preparation;
- Fraudulent E-mail Corpus single-file preparation.

The Fraudulent E-mail Corpus command must be exercised against real corpus content outside the repository, preferably in Kaggle or another isolated environment. Unit tests for that command use synthetic messages only.

---

## Isolated Kaggle Preparation Workflow

Some raw email corpora contain suspicious links, malware-themed attachment names, exploit-like text, scam content, or other indicators that can make direct local inspection unsuitable. The project should not disable local security protections to inspect those corpora.

When local raw inspection is unsuitable, use Kaggle Notebook or another isolated research environment to prepare the dataset.

The isolated workflow is:

1. Attach or download the raw dataset inside the isolated environment.
2. Read raw corpus bytes inside that environment.
3. Print only aggregate structural metrics, such as message counts, header counts, empty body counts, URL counts, charset issues, and output row counts.
4. Generate canonical PhishShield ML JSONL inside the isolated environment.
5. Validate the generated JSONL shape inside the isolated environment when practical.
6. Download only the generated JSONL to the approved local temporary dataset directory outside Git if local training is needed.
7. Run local validation again before training.

Do not copy raw email bodies, raw corpus excerpts, or real phishing/fraudulent samples into:

- the repository;
- unit tests;
- documentation;
- chat transcripts;
- issue descriptions.

Approved local storage pattern for generated datasets remains outside Git:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\<dataset-name>\prepared\
```

The Fraudulent E-mail Corpus used this workflow: raw corpus inspection and JSONL generation were performed in Kaggle Notebook, then the prepared JSONL was downloaded outside Git for local validation, training, and fixture holdout evaluation.

---

## Prepared Dataset Validation

The validation command checks prepared JSONL files before any training step.

Current validation covers:

- required fields;
- JSON parse errors;
- duplicate `sample_id` values;
- allowed normalized labels;
- list-shaped URL and attachment fields;
- object-shaped metadata;
- label distribution;
- empty subject and body counts;
- total extracted URL counts.

Example:

```text
python -m tools.ml_data_preparation.validate_prepared_dataset --input prepared/easy_ham.jsonl --input prepared/spam.jsonl
```

---

## PhishShield Fixture Holdout Samples

PhishShield fixtures can be prepared as holdout samples with `tools/ml_data_preparation/phishshield_fixtures.py`.

These samples are for evaluation only. They must not be mixed into training, validation, or test splits for the SpamAssassin baseline.

The fixture preparation tooling uses:

```text
source: phishshield-fixtures
source_uri: tests/fixtures/emails
```

Supported holdout labels:

```text
benign
suspicious
```

---

## Fraudulent E-mail Corpus Preparation

The Fraudulent E-mail Corpus can be prepared with:

```text
python -m tools.ml_data_preparation.prepare_fraudulent_email_corpus --input-file path/to/fradulent_emails.txt --output path/to/fraudulent_email_corpus.jsonl
```

The command expects the upstream single text file and writes canonical PhishShield ML JSONL rows.

The implementation reads the corpus as bytes, splits messages on ASCII email boundaries, and passes each raw message to the email parser without first decoding the whole file as UTF-8. This preserves mixed-encoding messages better than a whole-corpus text conversion.

The email parser also applies conservative fallbacks for non-standard charsets observed in the corpus, including `ansi`, `default`, `unknown-8bit`, `windows-125`, `x-user-defined`, and invalid charset names.

Preparation mapping:

```text
source: fraudulent_email_corpus
source_uri: https://www.kaggle.com/datasets/rtatman/fraudulent-email-corpus
original_label: fraud
normalized_label: suspicious
```

Operational rules:

- keep the raw corpus outside the repository;
- keep generated JSONL outputs outside the repository;
- run real-corpus preparation in Kaggle or another isolated environment when local handling is unsuitable;
- use synthetic messages only for committed unit tests;
- validate generated JSONL with `tools.ml_data_preparation.validate_prepared_dataset` before training.

The upstream filename observed in the Kaggle download is:

```text
fradulent_emails.txt
```

The misspelling is preserved by the upstream dataset and should be handled as the real input filename.

A Kaggle preparation test with charset fallback produced:

```text
discovered: 3906
processed: 3906
failed: 0
invalid_rows: 0
duplicate_sample_ids: 0
labels: suspicious=3906
empty_subject: 88
empty_body: 85
urls_found: 2161
output_bytes: 12984691
```

Local validation of the prepared JSONL after downloading it outside Git produced:

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

---

## Phishing Email Detection Preparation Candidate

The `Phishing Email Detection` CSV candidate was downloaded outside Git for schema and quality inspection:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\phishing-email-detection\raw\Phishing_Email.csv
```

Observed schema:

```text
columns: '', Email Text, Email Type
labels: Safe Email, Phishing Email
```

Planned label mapping for a controlled preparation POC:

```text
Safe Email -> benign
Phishing Email -> suspicious
```

Inspection summary:

```text
rows: 18650
parse_errors: 0
labels: Safe Email=11322, Phishing Email=7328
empty_text: 19
duplicate_text: 1127
short_rows_lt_30: 584
long_rows_gt_10000: 397
url_only_rows: 1
```

Required preparation behavior:

- keep the raw CSV and generated JSONL outside the repository;
- reject or report empty text rows;
- report duplicate text rows;
- report very short, very long, URL-only, and no-alpha rows;
- preserve the original label in metadata;
- map labels into `benign` and `suspicious` only after validating exact label strings;
- emit aggregate quality counters for spam-like and phishing-like keyword groups.

The dataset is approved for a controlled ingestion POC, but not as a clean phishing source. The first experiment must interpret results cautiously because the `Phishing Email` class contains noticeable spam-like marketing, adult, pharma, mortgage, stock, and investment language.

---

## First Local Dry Run Result

The first local dry run used a manually downloaded SpamAssassin subset stored outside the repository:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\spamassassin\raw
```

The preparation command was executed with `--limit 20` for both `easy_ham` and `spam`.

Results:

| Label | Processed | Failed | Empty subject | Empty body | URLs found |
|---|---:|---:|---:|---:|---:|
| `easy_ham` | 20 | 0 | 0 | 0 | 41 |
| `spam` | 20 | 0 | 0 | 0 | 53 |

Generated JSONL outputs were written outside the repository under:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\spamassassin\prepared
```

The dry run confirms that the current preparation command can process a small real SpamAssassin sample and produce canonical JSONL rows without adding raw corpora or generated datasets to Git.

---

## First Prepared Dataset Validation Result

The first prepared JSONL validation used the outputs from the local SpamAssassin dry run:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\spamassassin\prepared\easy_ham.jsonl
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\spamassassin\prepared\spam.jsonl
```

Command:

```text
python -m tools.ml_data_preparation.validate_prepared_dataset --input "C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\spamassassin\prepared\easy_ham.jsonl" --input "C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\spamassassin\prepared\spam.jsonl"
```

Result:

```text
files: 2
rows: 40
invalid_rows: 0
duplicate_sample_ids: 0
labels:
  benign: 20
  suspicious: 20
empty_subject: 0
empty_body: 0
urls_found: 94
```

The validation confirms that the first prepared sample has valid JSONL shape, no duplicate sample IDs, no invalid rows, and balanced labels for the small dry-run subset.

---

## Larger SpamAssassin Dry Run Result

A larger local dry run was executed against the manually downloaded SpamAssassin `easy_ham` and `spam` subsets outside the repository.

Preparation results:

| Output | Processed | Failed | Empty subject | Empty body | URLs found |
|---|---:|---:|---:|---:|---:|
| `easy_ham_full.jsonl` | 2501 | 0 | 1 | 0 | 4276 |
| `spam_full.jsonl` | 501 | 0 | 3 | 3 | 1123 |
| `easy_ham_1000.jsonl` | 1000 | 0 | 0 | 0 | 1384 |
| `spam_1000.jsonl` | 501 | 0 | 3 | 3 | 1123 |

Validation results for the full prepared outputs:

```text
files: 2
rows: 3002
invalid_rows: 0
duplicate_sample_ids: 0
labels:
  benign: 2501
  suspicious: 501
empty_subject: 4
empty_body: 3
urls_found: 5399
```

Validation results for the capped prepared outputs:

```text
files: 2
rows: 1501
invalid_rows: 0
duplicate_sample_ids: 0
labels:
  benign: 1000
  suspicious: 501
empty_subject: 3
empty_body: 3
urls_found: 2507
```

The larger dry run confirms that the current SpamAssassin preparation and validation tooling can process the available local subset without invalid rows or duplicate sample IDs. The class distribution is imbalanced in the full subset, so the first training baseline should either use a balanced subset or explicit class balancing.

---

## Next Implementation Questions

1. Should the first training baseline use a balanced subset or the full imbalanced SpamAssassin subset with class weighting?
2. What threshold should trigger investigation for invalid rows, duplicate sample IDs, empty subjects, or empty bodies?
3. Should the first normalized label target remain binary for the initial training baseline?
4. What exact truncation limits should apply to subject, body, URL list, and attachment filenames?
5. Where should generated prepared datasets live outside the Git repository for repeatable experiments?
