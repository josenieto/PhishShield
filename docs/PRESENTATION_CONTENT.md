# PhishShield Presentation

This document is the English content source for the public Google Slides
presentation. The final deck should use a 16:9 layout and keep one main message
per slide.

## Slide 1: PhishShield

### Local and Explainable Phishing Email Triage

With deterministic analysis and experimental AI assistance.

José Nieto Alaber
Máster en Desarrollo con IA · Big School
August 2026

Visual: use a minimal `.eml -> evidence -> risk` flow. Do not use a product
screenshot on the cover.

## Slide 2: The Problem

### A Reported Email Needs A Safe First Look

- Users report suspicious messages as `.eml` files.
- Opening the message in a normal mail client can expose analysts to links,
  attachments, and social-engineering content.
- Analysts need evidence before escalating a message.
- Sensitive email should not be sent to an untrusted cloud service just to obtain
  an initial assessment.

Key message: the first triage step should be safe, local, and explainable.

## Slide 3: Project Goal

### Local-First Triage For Analysts And Help-Desk Teams

PhishShield provides a reproducible first analysis of suspicious `.eml` files.

- Process messages locally.
- Extract technical and social-engineering indicators.
- Explain why each finding matters.
- Produce deterministic risk and exportable evidence.
- Keep optional AI assistance separate from the authoritative analysis.

## Slide 4: Core Workflow

### From Reported Message To Evidence

```text
Upload .eml
    -> extract sender, authentication, URLs, attachments, and text
    -> evaluate deterministic indicators
    -> review findings, evidence, and risk
    -> export Markdown, JSON, or HTML evidence
```

Visual: use a large horizontal workflow diagram. Do not add a small screenshot
just to fill the slide.

## Slide 5: Deterministic Risk And Evidence

### The Analyst Sees The Result And The Reason

Use one large, legible crop of `suspicious-analysis_1.png` and highlight:

- deterministic risk score, aggregated from multiple findings;
- SPF, DKIM, and DMARC results extracted from the email headers;
- report actions.

The authentication boxes are technical evidence from the message headers, not
AI predictions. The `CRITICAL` risk label is the deterministic result of the
combined findings.

## Slide 6: Architecture And Technology Stack

### A Modular Monolith With Clear Boundaries

```text
React / TypeScript / Vite
            |
        Nginx frontend
            |
       FastAPI backend
            |
Application use cases and ports
            |
Domain models, rules, evidence, and risk
```

Technology stack:

- Backend: Python, FastAPI, Pydantic.
- Frontend: React, TypeScript, Vite.
- Deployment: Docker, Docker Compose, GHCR.
- Quality: pytest, Vitest, GitHub Actions, pre-commit.
- AI advisory: scikit-learn, TF-IDF, Logistic Regression.

## Slide 7: Experimental AI-Assisted Assessment

### A Local Advisory Capability, Not An Automated Verdict

```text
.eml
  -> deterministic representation
  -> notification-family scope gate
  -> TF-IDF + Logistic Regression
  -> benign / suspicious / inconclusive
```

- Optional and disabled by default.
- Local model assessment with explicit configuration.
- Abstains when the message is out of scope or confidence is insufficient.
- Does not modify deterministic findings, evidence, or `risk_score`.
- Does not act as a CI gate or replace analyst judgment.

## Slide 8: Why The AI Remains Experimental

### Evidence Quality Sets The Promotion Boundary

The model is not promoted to the main product path because the project does not
yet have an authorized, representative, family-labeled, and independently
validated corpus suitable for deployment decisions.

- Real email can contain personal, confidential, or operationally sensitive
  information.
- Public corpora can be historically limited or non-representative.
- Training, calibration, regression, and promotion data must remain separated.
- Validation must cover families, time periods, false positives, and false
  negatives.
- Out-of-distribution messages require abstention rather than overconfident
  classification.

Key message: limiting the model is a safety decision, not an absence of work.

## Slide 9: Delivery, Impact And Future Work

### A Public, Reproducible Foundation For Further Validation

- Public repository: `github.com/josenieto/PhishShield`.
- Local execution through Docker Compose and versioned GHCR images.
- Safe synthetic sample for a repeatable demonstration.
- Community feedback channel and public project documentation.
- Current limitation: no representative authorized corpus for model promotion.

Future work:

- Build or obtain an authorized and privacy-preserving corpus.
- Improve family coverage and independent temporal validation.
- Define explicit model promotion thresholds.
- Preserve deterministic-first behavior and abstention safeguards.

Closing message: PhishShield demonstrates a practical security tool and a
responsible path toward AI-assisted triage.
