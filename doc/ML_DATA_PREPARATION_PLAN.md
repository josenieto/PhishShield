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
- general parsing scripts beyond the initial SpamAssassin preparation command;
- training scripts;
- model artifacts;
- model runtime dependencies;
- API or frontend changes;
- automatic dataset redistribution.

---

## Next Implementation Questions

1. Which real SpamAssassin subset should be used for the first local ingestion dry run outside Git?
2. Should the first normalized label target be binary or multi-class?
3. Which fields should be mandatory for a valid prepared sample?
4. What exact truncation limits should apply to subject, body, URL list, and attachment filenames?
5. Where should generated prepared datasets live outside the Git repository?
