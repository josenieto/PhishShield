# ML Dataset Research

## Purpose

This document records the initial dataset research for future model-assisted email analysis in PhishShield.

Its goal is to identify realistic public corpora that could support a project-owned phishing email model without requiring users to install an external AI runtime.

This document is intentionally about data and evaluation planning. It does not introduce model training or inference implementation yet.

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
- spam and noise baseline;
- stress-testing whether a future classifier collapses phishing into generic spam.

Important caveats:

- the corpus is old;
- it is better suited to generic spam filtering than phishing-specific detection;
- dataset cleaning and feature strategy should avoid learning only era-specific artifacts.

### Enron Email Dataset

Reference:

```text
https://www.cs.cmu.edu/~enron/
```

Potential use:

- benign corporate email language;
- realistic business writing style;
- evaluation against normal internal and operational communication.

Important caveats:

- privacy and PII sensitivity remain important even though the corpus is public;
- attachments are not included in the main published version;
- the host site itself warns about sensitivity and documents later concerns about authenticity and integrity in some parts of the corpus;
- careful filtering, deduplication, and ethical handling are required.

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

Potential use:

- complementary fraud and social-engineering language;
- non-credential fraudulent persuasion patterns.

Important caveats:

- may not represent modern credential phishing or account-verification lures well;
- should not be treated as a direct substitute for phishing email corpora.

### Kaggle Phishing Email Datasets

Potential use:

- exploratory candidate data sources;
- supplementary research if provenance is acceptable.

Important caveats:

- many datasets have unclear lineage or licensing;
- duplicates and synthetic rows are common;
- labels may be inconsistent;
- they should be manually audited before inclusion in any training plan.

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

## Next Dataset Candidate Decision

The next dataset candidate to investigate is the Fraudulent E-mail Corpus.

This is a research selection, not approval to train on or redistribute the corpus. Access, licensing, format, and privacy risk still need to be confirmed before any ingestion prototype is added.

Reasons for selecting it next:

- the SpamAssassin-only baseline already validated the ML pipeline mechanics but did not transfer well to PhishShield phishing fixtures;
- the corpus is more aligned with fraud and social-engineering language than generic spam corpora;
- the currently known Nazario access path returned `403 Forbidden`, so it is blocked until a trustworthy source and license are confirmed;
- Kaggle datasets remain deferred because provenance, license, duplicates, synthetic rows, and label quality vary widely.

Expected investigation outcome:

- confirm whether the corpus can be accessed from a stable source;
- record license and redistribution constraints;
- inspect message format and label structure;
- identify PII or sensitive-content handling requirements;
- decide whether a small ingestion prototype is justified.

The corpus should be treated as a phishing-adjacent fraud and social-engineering source. It should not be treated as a complete substitute for modern credential-phishing data.

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
