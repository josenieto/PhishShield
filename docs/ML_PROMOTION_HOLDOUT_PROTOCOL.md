# ML Promotion Holdout Protocol

## Purpose

This protocol defines the independent evidence required before PhishShield's
advisory email model can be treated as product-ready for any email family.
The model remains optional, advisory, and separate from deterministic findings
and risk scoring until this protocol is satisfied.

## Target Set

The initial promotion holdout contains 320 reviewed English email samples:

```text
8 families * 20 benign * 20 suspicious = 320 samples
```

Families:

- `account`
- `mfa_security`
- `cloud_document_sharing`
- `billing_invoices`
- `support`
- `hr`
- `vendor_portals`
- `newsletter_preferences`

Each family is evaluated independently. Aggregate results cannot compensate
for a failed family.

## Admitted Evidence

Samples may come from public reports, campaign repositories, or other public
evidence when the source preserves enough information to construct the frozen
model representation:

```text
subject + body_text + urls + attachment_filenames
```

The original `.eml` is preferred but not required. Text evidence without the
original message must record `raw_available: false`.

Every sample requires:

- a stable source URI;
- source and license or terms-of-use record;
- English-language content;
- reviewed benign or suspicious label;
- reviewed family assignment;
- collection date;
- SHA-256 content hash;
- explicit review status;
- no unauthorized sensitive personal information.

Exclude URL-only samples, summaries without message text, screenshots without
extractable text, unreviewed labels, and messages outside the declared family.

## Independence Rules

The holdout must remain separate from:

- `Phishing Email Detection`;
- synthetic benign and suspicious notification datasets;
- SpamAssassin and Enron calibration data;
- CEAS-08;
- Darkknight;
- PhishShield fixtures;
- aggregated corpora that contain any of these sources.

Exact and near-duplicate samples are excluded. The holdout must not be used
for training, calibration, feature selection, or threshold selection after
evaluation begins.

## Manifest

The versioned manifest template is:

```text
config/ml/promotion_holdout_manifest.template.jsonl
```

The manifest contains provenance and audit metadata only. Raw messages,
prepared JSONL, predictions, and detailed evaluation outputs remain outside Git
under:

```text
<PHISHSHIELD_DATA_ROOT>\promotion-holdout\
```

The validator requires exactly 20 benign and 20 suspicious samples for every
family before a manifest can be accepted.

## Approved Promotion Thresholds

The thresholds were approved before collecting holdout samples:

- coverage of at least `70%`, with at least 28 conclusive predictions;
- conditional accuracy of at least `95%`;
- no more than `1` confident false positive among 20 benign samples;
- no more than `1` confident false negative among 20 suspicious samples;
- no regression in confident errors on the 32 PhishShield fixtures.

These thresholds are implemented in
`tools/ml_training/promotion_policy.py`. A family that fails one threshold is
classified as experimental or out of scope; aggregate performance cannot
override the family result.

## Source Curation

Candidate sources must first be recorded in:

```text
config/ml/promotion_holdout_sources.template.jsonl
```

The source record is not admission evidence by itself. Samples can only enter
the promotion manifest after provenance, terms, privacy, independence, and
content-quality review are complete.

## Evaluation

Use the frozen candidate input contract and conservative abstention policy.
Report these values globally and by family:

- coverage;
- abstention rate;
- conditional accuracy;
- confident false-positive rate;
- confident false-negative rate;
- counts of inconclusive predictions.

The model must also preserve the existing PhishShield fixture regression
behavior. A family that lacks sufficient coverage or exceeds an approved error
limit remains experimental and is not promoted.

Promotion thresholds must be approved before inspecting the holdout results.
This protocol does not itself promote a model or define a universal phishing
verdict.
