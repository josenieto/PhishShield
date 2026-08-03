# ML Dataset Research

## Purpose

This document records the initial dataset research for future model-assisted email analysis in PhishShield.

Its goal is to identify realistic public corpora that could support a project-owned phishing email model without requiring users to install an external AI runtime.

This document is intentionally about data and evaluation planning. It does not introduce model training or inference implementation yet.

## Dataset Usage Registry

This registry records whether each researched source was used for training,
calibration, regression holdout, or independent diagnostic evaluation. Raw and
prepared datasets remain outside Git.

| Dataset | Usage | Status | License | Training use | Holdout use | Decision |
|---|---|---|---|---|---|---|
| Apache SpamAssassin Public Corpus | Ham/spam baseline and benign calibration | Used | Source terms require review | Historical yes | No | Reject as a phishing-quality model by itself. |
| Fraudulent E-mail Corpus | Fraud/social-engineering baseline | Used | `CC BY-SA 4.0` | Historical yes | No | Reject as sufficient modern phishing coverage. |
| Phishing Email Detection | Main phishing text baseline | Used | `LGPL-3.0` declared by source mirror | Yes | No | Current candidate training source. |
| SpamAssassin `hard_ham` | Benign calibration | Used | SpamAssassin source terms | Historical yes | No | Did not improve notification-like benign calibration. |
| Enron Email Dataset | Benign business-email calibration POC | Used | Public source with privacy and integrity concerns | Historical POC only | No | Did not improve current holdout; do not redistribute. |
| Synthetic benign notifications | Targeted calibration | Generated | Project-authored | Yes | No | Useful only as controlled calibration, not independent evidence. |
| Synthetic suspicious notifications | Balanced calibration | Generated | Project-authored | Yes | No | Useful only as controlled calibration, not independent evidence. |
| PhishShield fixtures | Regression and qualitative holdout | Used | Project | No | Yes | Must remain outside training and is not independent promotion evidence. |
| `darkknight25/phishing_benign_email_dataset` | External diagnostic text holdout | Evaluated | `MIT` declared by source | No | Yes | Small and likely curated; not sufficient for promotion alone. |
| `cybersectony/PhishingEmailDetectionv2.0` | Future email-only research candidate | Inspected, not downloaded | Not clearly declared | No | No | Requires provenance, license, filtering and overlap review. |
| `Phishing Email Curated Cleaned` | Future benchmark candidate | Inspected, not downloaded | `CC BY 4.0` declared by source | No | No | Not independent because it aggregates previously used corpora. |

### Registry Rules

- A source used for training or calibration cannot later be called an independent promotion holdout.
- PhishShield fixtures are regression evidence, not independent product-promotion evidence.
- Raw corpora, prepared JSONL, holdout manifests, per-sample predictions, and model artifacts remain outside Git.
- Every new source requires license, provenance, schema, quality, privacy, and overlap review.
- Evaluation reports must state whether the result is diagnostic, calibration, regression, or promotion evidence.
- External text holdouts must use the same model input representation as the candidate being evaluated. Source metadata such as intent, technique, target, and spoofed sender is retained only for error analysis unless it is explicitly part of a new training feature contract.

---

## Selection Criteria

Candidate datasets should be evaluated against these questions:

- Is the dataset publicly available for research or open-source use?
- Is the license clear enough for internal research and possible later packaging decisions?
- Does the dataset contain real email messages or only metadata or URLs?
- Does it represent benign corporate email, spam, fraud, phishing, or a mixture?
- Is the dataset old enough that artifacts or outdated tactics may dominate?
- Does it contain privacy, integrity, or authenticity concerns that require extra caution?
- Can the dataset support a clean train, validation, and test strategy without obvious leakage?

---

## Candidate Dataset Matrix

| Dataset | Primary use | Strength | Main risk |
|---|---|---|---|
| Apache SpamAssassin Public Corpus | ham/spam baseline | Public and well-known corpus with separate ham and spam groups. | Old and not phishing-specific. |
| Enron Email Dataset | benign corporate email | Large corpus of realistic business email language. | Privacy sensitivity, cleanup needs, and known integrity concerns. |
| TREC Spam Track corpora | spam/ham evaluation | Established academic benchmark for email classification. | Availability and licensing need verification; spam is not phishing. |
| Nazario Phishing Corpus | phishing examples | Historically phishing-specific and directly relevant. | Current access, licensing, and age require validation. |
| Fraudulent E-mail Corpus | fraud and social engineering | Useful for persuasion and fraud-style language patterns. | Not necessarily modern credential-phishing behavior. |
| Phishing Email Detection | phishing and safe email text | Public labeled email-text dataset with phishing and safe email classes. | Not raw `.eml`; provenance and content quality need inspection before training. |
| PhishingEmailDetectionv2.0 | email and URL phishing classification | Large modern text dataset with explicit email and URL classes. | Mixed email/URL corpus; email rows must be isolated before use. |
| Phishing Email Curated Cleaned | aggregated phishing/spam/legitimate corpus | Large cleaned benchmark aggregating public corpora across 1995-2022. | Aggregated and transformed; source overlap, leakage, and license compatibility need careful review. |
| Kaggle phishing email datasets | candidate phishing/fraud data | Easy discovery and potential variety. | Provenance, license, deduplication, and label quality vary widely. |

---

## Dataset Notes

### Apache SpamAssassin Public Corpus

Reference:

```text
https://spamassassin.apache.org/old/publiccorpus/
```

Observed structure includes:

- `easy_ham`
- `hard_ham`
- `spam`

Potential use:

- ham baseline;
- first low-friction benign calibration source through `hard_ham`;
- spam and noise baseline;
- stress-testing whether a future classifier collapses phishing into generic spam.

Important caveats:

- the corpus is old;
- it is better suited to generic spam filtering than phishing-specific detection;
- `hard_ham` may improve difficult benign calibration but is still not a substitute for realistic business/account/security notifications;
- dataset cleaning and feature strategy should avoid learning only era-specific artifacts.

### Enron Email Dataset

Reference:

```text
https://www.cs.cmu.edu/~enron/
```

Recommended upstream version:

```text
https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz
```

Observed source notes:

- the corpus contains about `0.5M` messages;
- messages are organized into folders for about `150` users, mostly senior Enron management;
- the current upstream page recommends the May 7, 2015 version and states that prior versions are no longer distributed;
- the distributed CMU version does not include attachments;
- some messages were deleted as part of a redaction effort;
- invalid email addresses were normalized where possible;
- the page explicitly asks researchers to be sensitive to the privacy of the people involved;
- the page also documents later concerns about authenticity and integrity for some parts of the corpus.

Potential use:

- benign corporate email language;
- realistic business writing style;
- evaluation against normal internal and operational communication.

Important caveats:

- privacy and PII sensitivity remain important even though the corpus is public;
- attachments are not included in the main published version;
- the host site itself warns about sensitivity and documents later concerns about authenticity and integrity in some parts of the corpus;
- careful filtering, deduplication, and ethical handling are required.

Current decision:

- selected as the next benign business-email calibration candidate after SpamAssassin `hard_ham` failed to improve the expanded holdout;
- approved only for workflow planning and a capped preparation POC after privacy and cleanup controls are documented;
- not approved for broad ingestion, committed raw data, committed prepared data, model artifacts, or inference integration.

### TREC Spam Track Corpora

Reference:

```text
https://trec.nist.gov/data/spam.html
```

Potential use:

- baseline spam and ham evaluation;
- comparison corpus for classical text classification experiments.

Important caveats:

- availability and exact usage conditions should be checked before use;
- it still models spam filtering more than modern phishing email assessment.

### Nazario Phishing Corpus

Historical reference path attempted during research:

```text
https://monkey.org/~jose/wiki/doku.php?id=PhishingCorpus
```

Observed issue:

- direct access returned `403 Forbidden` during this research pass.

Potential use:

- phishing-specific positive class if an acceptable mirror or documented source can be confirmed.

Important caveats:

- dataset age;
- uncertain current distribution path;
- licensing and redistribution terms need explicit confirmation.

### Fraudulent E-mail Corpus

Reference:

```text
https://www.kaggle.com/datasets/rtatman/fraudulent-email-corpus
```

Observed Kaggle metadata during research:

- Kaggle ref: `rtatman/fraudulent-email-corpus`;
- owner: `rtatman`;
- title: `Fraudulent E-mail Corpus`;
- license: `CC BY-SA 4.0`;
- size: approximately 17.3 MB;
- described source: CLAIR collection of fraud email;
- citation requested by dataset notes: `Radev, D. (2008), CLAIR collection of fraud email, ACL Data and Code Repository, ADCR2008T001`;
- described content: more than 2,500 Nigerian or 419 fraud letters from 1998 to 2007;
- described format: a single text file containing messages with email-like headers.

Local download observation:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\fraudulent-email-corpus\fradulent_emails.txt
```

The downloaded file exists outside the repository and matches the expected approximate size. The filename uses the upstream spelling `fradulent_emails.txt`.

Preparation status:

- ingestion support exists as project tooling under `tools/ml_data_preparation/`;
- tests use synthetic messages that mimic the corpus shape and do not include raw corpus content;
- preparation preserves raw message bytes before handing each message to the email parser, which avoids a whole-corpus UTF-8 decode pass;
- non-standard message charsets observed in the corpus are handled with a conservative Windows-1252 fallback;
- real corpus preparation was performed through the isolated Kaggle Notebook workflow because direct local raw corpus inspection was unsuitable for this content type;
- generated JSONL outputs must remain outside the repository.

Workflow note:

- raw corpus bytes were inspected only in Kaggle Notebook;
- only aggregate structure and validation metrics were recorded in project documentation;
- the prepared JSONL was downloaded to the approved temporary dataset directory outside Git;
- raw email bodies and real fraudulent samples were not copied into tests, docs, or repository files.

Structural inspection in Kaggle found:

```text
bytes: 17344435
messages_detected: 3906
replacement_chars_from_naive_utf8_decode: 10524
subjects: 3839
empty_subjects: 21
unique_subjects: 2503
empty_bodies: 52
http_urls_in_bodies: 2781
email_like_tokens_total: 20059
largest_body_chars: 608258
```

The inspection confirms that the dataset is large enough and structurally parseable for controlled fraud/social-engineering experiments. It also confirms that whole-file UTF-8 decoding is not appropriate because the corpus contains mixed encodings.

A follow-up Kaggle preparation test with charset fallback produced:

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

This confirms that non-standard charsets such as `ansi`, `default`, `unknown-8bit`, `windows-125`, `x-user-defined`, and malformed charset names should not block preparation.

Potential use:

- complementary fraud and social-engineering language;
- non-credential fraudulent persuasion patterns.

Important caveats:

- may not represent modern credential phishing or account-verification lures well;
- should not be treated as a direct substitute for phishing email corpora.

Current decision:

- approved for controlled preparation experiments outside the repository;
- acceptable for suspicious fraud/social-engineering training experiments if license and attribution requirements are followed;
- not yet approved for committed raw data, generated artifacts, or runtime inference integration.

### Kaggle Phishing Email Datasets

Potential use:

- exploratory candidate data sources;
- supplementary research if provenance is acceptable.

Important caveats:

- many datasets have unclear lineage or licensing;
- duplicates and synthetic rows are common;
- labels may be inconsistent;
- they should be manually audited before inclusion in any training plan.

### Phishing Email Detection

Primary reference:

```text
https://www.kaggle.com/datasets/subhajournal/phishingemails
```

Hugging Face mirror inspected during research:

```text
https://huggingface.co/datasets/zefang-liu/phishing-email-dataset
```

Observed metadata:

- Kaggle ref: `subhajournal/phishingemails`;
- Kaggle owner: `subhajournal` / `Cyber Cop`;
- Hugging Face mirror: `zefang-liu/phishing-email-dataset`;
- license: `GNU Lesser General Public License 3.0`;
- size: approximately 52 MB on Kaggle;
- Hugging Face mirror format: CSV;
- Hugging Face mirror rows: approximately 18.7k;
- mirror file: `Phishing_Email.csv`;
- visible columns: `Email Text` and `Email Type`;
- visible labels: `Safe Email` and `Phishing Email`.

Potential use:

- next phishing-specific suspicious source for baseline experiments;
- text-only or text-plus-light-metadata preparation once columns and labels are validated;
- candidate replacement for generic spam or 419 fraud as the suspicious class.

Important caveats:

- not raw `.eml`, so it cannot exercise parser behavior, MIME handling, or original headers;
- sender, receiver, attachment, and authentication metadata appear unavailable in the visible mirror;
- visible preview includes phishing, spam-like marketing, URL-heavy messages, and safe operational/business email, so class quality must be audited;
- license compatibility and attribution requirements must be reviewed before any packaging or artifact decisions;
- source overlap with existing public corpora and PhishShield holdout leakage risk must be checked.

Current decision:

- selected as the next modern phishing email dataset candidate for access, license, format, and quality verification;
- approved for a controlled ingestion POC with mandatory cleaning after local inspection confirmed parseable CSV structure and usable labels;
- not approved for model artifacts or inference integration.

Local schema and quality inspection used the manually downloaded CSV stored outside the repository:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\phishing-email-detection\raw\Phishing_Email.csv
```

Inspection result:

```text
bytes: 52034604
columns: '', Email Text, Email Type
rows: 18650
parse_errors: 0
labels: Safe Email=11322, Phishing Email=7328
null_text: 0
empty_text: 19
duplicate_text: 1127
duplicate_text_ratio: 0.0604
short_rows_lt_30: 584
long_rows_gt_10000: 397
url_only_rows: 1
no_alpha_rows: 1
```

Per-label quality notes:

```text
Phishing Email: rows=7328, empty_text=19, duplicate_text=783, short_rows_lt_30=374, long_rows_gt_10000=137, url_only_rows=0
Safe Email: rows=11322, empty_text=0, duplicate_text=344, short_rows_lt_30=210, long_rows_gt_10000=260, url_only_rows=1
```

The dataset is usable for a preparation prototype, but it is not a clean modern phishing corpus. The `Phishing Email` class includes many spam-like and marketing/adult/pharma/stock terms, so the first ingestion must include filtering or at least explicit quality counters for empty, duplicate, very short, very long, URL-only, and spam-like rows.

### CEAS-08 Subset From Phishing Email Curated Datasets

Reference:

```text
Zenodo record: https://doi.org/10.5281/zenodo.8339691
Source file: CEAS_08.csv
License declared by record: CC-BY-4.0
```

The CEAS-08 CSV was downloaded manually outside Git for a controlled preparation
POC. It contains sender, receiver, date, subject, body, label, and a source URL
flag. The source file is not approved for training or calibration at this stage.

Preparation result:

```text
rows_read: 39154
processed: 39154
failed: 0
unsupported_label: 0
empty_subject: 28
empty_body: 0
duplicate_content: 54
labels: benign=17312, suspicious=21842
urls_found: 130957
```

Prepared output remains outside Git:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\ceas-08\prepared\ceas_08.jsonl
```

Observed label mapping:

```text
0 -> benign
1 -> suspicious
```

Audit metadata preserves sender, receiver, date, original label, and the source
URL flag, but those fields are not model features. The feature representation
remains `subject + body_text + urls + attachment_filenames`.

Exact subject/body/URL overlap against current training inputs was previously zero.
Near-duplicate and source-overlap analysis is still required before this source
can be called an independent promotion holdout.

Current decision:

```text
approved for controlled external evaluation preparation;
not approved for training or calibration;
not yet approved as final product-promotion evidence.
```

### PhishingEmailDetectionv2.0

Reference:

```text
https://huggingface.co/datasets/cybersectony/PhishingEmailDetectionv2.0
```

Observed metadata:

- owner: `cybersectony`;
- format: Parquet;
- total samples: 200,000;
- described split: 22,644 email samples and 177,356 URL samples;
- visible columns: `content` and `label`;
- labels described as `legitimate_email`, `phishing_email`, `legitimate_url`, and `phishing_url`;
- license was not visible in the inspected metadata response.

Potential use:

- auxiliary source if email rows can be isolated reliably;
- useful for checking whether a larger mixed email/URL dataset improves phishing recall.

Important caveats:

- most rows are URLs rather than emails;
- email and URL rows must not be mixed for the first email-text baseline;
- license and provenance must be clarified before use;
- several Hugging Face copies exist, so source identity and duplication need review.

Current decision:

- keep as secondary candidate;
- do not use before the `Phishing Email Detection` CSV candidate is inspected.

### Phishing Email Curated Cleaned

Reference:

```text
https://huggingface.co/datasets/it4lia/PhishingEmailCuratedDatasets_Cleaned
```

Observed metadata:

- license: `cc-by-4.0`;
- format: Parquet plus NumPy artifacts;
- rows: approximately 182k;
- described as a cleaned AI-ready version of the original Phishing Email Curated Datasets aggregation;
- source coverage described as 11 heterogeneous public email corpora spanning 1995-2022;
- visible fields include `label_int`, `label_str`, source identifiers, sender, receiver, date, subject, URL flags, deduplication fields, and content-derived hashes.

Potential use:

- future benchmark or source-aware experiment after stronger provenance review;
- useful for deduplication and source-group split research.

Important caveats:

- aggregated and transformed dataset, so leakage and duplicate-source handling are central risks;
- appears to include older corpora already considered, such as Nazario, Nigerian Fraud, SpamAssassin, Enron, Ling-Spam, and CEAS-08;
- content visibility and exact text fields need inspection before any ingestion decision;
- because it aggregates multiple corpora, it should not be the first next POC unless simpler sources fail.

Current decision:

- keep as later benchmark candidate;
- defer ingestion until source overlap and leakage controls are designed.

---

## Recommended Initial Dataset Mix

The safest initial direction is to avoid depending on a single corpus.

Recommended mix:

- benign baseline:
  - Enron after careful cleaning;
  - SpamAssassin `easy_ham` and `hard_ham`;
  - curated benign PhishShield fixtures for realistic holdout checks.
- suspicious and phishing baseline:
  - Nazario or another phishing-specific corpus if a trustworthy source is confirmed;
  - Fraudulent E-mail Corpus for social-engineering overlap;
  - carefully audited Kaggle samples only if provenance and licensing are acceptable.
- spam and noise baseline:
  - SpamAssassin spam;
  - TREC spam corpora if access and license are confirmed.

This mix supports a future classifier that distinguishes:

- benign operational email;
- generic spam and noise;
- phishing and phishing-like fraud.

---

## Benign Calibration Source Decision

The next benign calibration source to investigate is SpamAssassin `hard_ham`.

This follows the expanded fixture holdout and threshold sweep for the `Phishing Email Detection` baseline:

```text
expanded holdout: accuracy=0.6250, false_positive_benign=6, false_negative_suspicious=0
threshold sweep: no tested threshold improved the expanded holdout
```

Reason for selecting `hard_ham` first:

- it is available from the same public SpamAssassin corpus family already used by the project;
- existing SpamAssassin preparation tooling can likely process it with minimal code changes;
- it provides harder benign examples than `easy_ham`, which is useful for reducing false positives;
- it is a lower-friction calibration experiment than starting with Enron cleanup.

Expected limitations:

- it is old;
- it may still lack modern account, MFA, cloud-share, invoice, and newsletter notification patterns;
- it may include mailing-list or spam-adjacent benign content rather than business SaaS notifications;
- any improvement must be validated against the expanded PhishShield fixture holdout.

Secondary benign candidate:

- Enron Email Dataset, because it offers realistic business email language.

Enron was deferred until a privacy, PII, cleanup, deduplication, and source-integrity review was planned. After `hard_ham` failed to improve benign calibration, Enron is now the next benign calibration workflow candidate.

Current decision:

- use SpamAssassin `hard_ham` as the first benign calibration candidate;
- plan Enron as the richer but higher-risk follow-up candidate;
- keep model artifact and inference adapter work blocked until benign false positives improve on the expanded holdout.

The first Enron step should be a capped POC, not broad ingestion.

---

## Next Dataset Candidate Decision

The next dataset candidate to investigate is `Phishing Email Detection` (`subhajournal/phishingemails`) and its Hugging Face mirror `zefang-liu/phishing-email-dataset`.

This is a research selection after the SpamAssassin-only and Fraudulent E-mail Corpus baselines both failed to improve PhishShield fixture holdout accuracy. It is not approval to train on, redistribute, package, or create model artifacts from the dataset.

Reasons for selecting it next:

- it contains labeled email text rather than only URLs or webpage features;
- it has explicit safe and phishing email labels;
- it is closer to credential and email-text phishing than generic spam or 419 fraud;
- it has a visible license (`LGPL-3.0`) and a public Kaggle source plus Hugging Face mirror;
- it is small enough for a controlled preparation POC before considering larger mixed corpora.

Expected investigation outcome:

- confirm the downloaded file name and schema;
- map `Safe Email` and `Phishing Email` into PhishShield normalized labels;
- inspect duplicate, empty, null, URL-only, and spam-like rows;
- decide whether the source is good enough for a controlled ingestion POC;
- keep the PhishShield fixture holdout outside training.

Inspection completed and confirmed a controlled ingestion POC is justified, with mandatory cleaning and quality reporting. The POC must not treat the dataset as a clean phishing source.

Secondary candidates remain `PhishingEmailDetectionv2.0` for a later email-row-only experiment and `Phishing Email Curated Cleaned` for source-aware benchmarking after leakage controls are designed.

---

## Baseline Model Recommendation

The first useful model should be simple and cheap before any heavier model is attempted.

Recommended baseline:

```text
TF-IDF + Logistic Regression
```

Alternative baseline:

```text
TF-IDF + Linear SVM
```

Why start here:

- easy to train and evaluate;
- low infrastructure cost;
- good baseline for phishing-vs-benign text classification;
- simpler to reason about than jumping directly to heavier local model runtimes.

Heavier candidates such as DistilBERT or MiniLM can be explored later if the baseline proves insufficient.

---

## Training And Evaluation Strategy

Recommended sequence:

1. Build a clean benign, phishing, and spam candidate dataset inventory.
2. Deduplicate aggressively.
3. Separate train, validation, and test sets by message identity and, when possible, by source group to reduce leakage.
4. Keep PhishShield's own realistic fixtures out of training and use them as a lightweight qualitative holdout set.
5. Evaluate not only accuracy, but also:
   - precision;
   - recall;
   - false positives on benign business email;
   - false negatives on subtle phishing lures.

The deterministic engine should remain the main evidence source regardless of model quality.

Detailed preparation rules are defined in:

- `doc/ML_DATA_PREPARATION_PLAN.md`

---

## Data Handling Rules

- Treat all raw email datasets as potentially sensitive.
- Avoid redistributing public corpora inside the repository unless licensing is explicitly compatible and storage is justified.
- Prefer documenting download sources and preprocessing steps over committing raw corpora.
- Keep dataset preparation reproducible when the project moves from planning to implementation.

---

## Known Risks

- **Age:** many public corpora are old and may bias the model toward outdated phishing or spam artifacts.
- **Privacy:** public does not mean consequence-free; Enron especially requires careful handling.
- **Integrity:** some corpora, including Enron, have documented authenticity concerns in some contexts.
- **Label quality:** crowdsourced or aggregated datasets may contain noisy labels.
- **Leakage:** repeated templates, mirrored messages, or shared headers can inflate evaluation results.
- **Task mismatch:** spam filtering corpora are not automatically good phishing corpora.

---

## Deferred Questions

These questions remain open until the project explicitly starts model training:

1. Which phishing-specific corpus is trustworthy enough to serve as the primary positive class?
2. Should the first model be binary (`benign` vs `phishing`) or multi-class (`benign`, `spam`, `phishing`)?
3. Should attachments and structured headers contribute to the first model input, or should it remain text-first?
4. What artifact format should the project own and package later: plain Python model files, ONNX, or another embedded format?

---

## Fixture Holdout Implication

The first holdout evaluation against PhishShield fixtures showed that a SpamAssassin-only ham/spam baseline is not sufficient for phishing model quality.

The next dataset step should prioritize phishing-specific corpora and benign business-email sources before any model artifact or inference adapter work.
