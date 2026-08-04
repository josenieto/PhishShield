# Promotion Holdout Curation Assessment

## Decision

The first public-source curation pass does not provide enough independent,
reproducible material to assemble the approved 320-sample promotion holdout.
The advisory model therefore remains `experimental_advisory`; no family is
promoted to product-ready inference.

This is a data-evidence decision, not a model-performance result. No public
sample was admitted merely to reach the target count.

## Sources Reviewed

### Phishing.Database

Source:

```text
https://github.com/Phishing-Database/Phishing.Database
```

The repository provides phishing domains, links, IPs, and threat feeds. It does
not provide complete email subjects and bodies suitable for the frozen model
representation. It is therefore rejected for this holdout as URL-only
evidence.

Decision: `rejected_url_only`.

### CISA Cybersecurity Advisories

Source:

```text
https://www.cisa.gov/news-events/cybersecurity-advisories
```

CISA publishes authoritative threat reports and campaign descriptions. The
reviewed index provides advisories and narrative threat intelligence, not a
balanced corpus of original email messages with stable subject/body records.
Individual reports may support threat-family research, but they cannot supply
promotion samples without an additional source preserving the actual message
content and terms permitting research use.

Decision: `candidate_context_only`.

### MITRE ATT&CK STIX Data

Source:

```text
https://github.com/mitre-attack/attack-stix-data
```

The repository contains ATT&CK techniques and threat-intelligence objects. It
is not an email-message corpus and does not provide the required benign and
suspicious subject/body pairs.

Decision: `rejected_not_email_corpus`.

### Vendor and incident-response reports

Security vendors and incident-response organizations publish useful phishing
campaign reports, but the common format is a screenshot, a redacted excerpt,
or a narrative description. Such material often lacks a stable text
transcription, complete URLs, licensing clarity, or enough benign counterparts
to support a balanced eight-family holdout. It can be useful for future
qualitative regression fixtures, not for this promotion gate without a
sample-by-sample provenance review.

Decision: `candidate_context_only` until complete message evidence and terms
are verified.

## Missing Evidence

The curation pass cannot currently establish all of the following at the
required scale:

- 160 independent benign notification messages;
- 160 independent suspicious notification messages;
- 20 benign and 20 suspicious messages in each declared family;
- exact and near-duplicate independence from training and diagnostic sources;
- reproducible subject/body text for every admitted sample;
- source terms that permit the intended research use;
- a defensible privacy review for every message.

Synthetic notifications cannot fill this gap because they are already used for
calibration. CEAS-08, Darkknight, Phishing Email Detection, SpamAssassin,
Enron, and PhishShield fixtures are excluded by the protocol.

## Final Checkpoint

The current evidence supports the following scope only:

- deterministic analysis remains authoritative;
- model assessment remains optional, disabled by default, and advisory;
- abstention-aware evaluation remains available for diagnostic and regression
  use;
- no product-facing promotion claim is made;
- no additional model-training iteration is justified by this source pass.

The 320-sample protocol remains documented as a future research requirement.
It must not be marked complete using URL feeds, synthetic samples, duplicated
public corpora, or unverified report excerpts.
