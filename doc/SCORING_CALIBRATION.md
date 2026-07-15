# Scoring Calibration Baseline

## Purpose

This document captures the current MVP scoring baseline for PhishShield using realistic `.eml` fixtures.

Its goal is to make score tuning evidence-driven. New scoring changes should follow fixture observations rather than intuition alone.

This baseline is intentionally small and practical. It is not a formal benchmark suite yet.

---

## Current Calibration Rule

Use this rule before changing weights or critical indicators:

1. Add or update realistic fixtures.
2. Observe the current result.
3. Decide whether the problem is caused by:
   - overly broad detection terms;
   - missing or weak signals;
   - scoring weights;
   - critical-indicator selection.
4. Prefer the smallest change that fixes the observed behavior.

Do not change scoring weights without fixture evidence.

---

## Current Fixture Baseline

| Fixture | Classification intent | Current result | Notes |
|---|---|---|---|
| `benign_account_summary.eml` | Benign | `LOW` | Clean baseline with passing authentication and no suspicious signals. |
| `benign_newsletter_weekly_digest.eml` | Benign | `LOW` | Newsletter-style content stays clean despite containing a normal HTTPS link. |
| `benign_security_alert_login_notice.eml` | Benign | `LOW` | Legitimate security wording does not create critical or elevated risk on its own. |
| `benign_password_reset_notice.eml` | Benign | `LOW` | Previously over-triggered due to the generic `password` term; now clean after narrowing credential-request phrases. |
| `benign_invoice_with_pdf.eml` | Benign | `LOW` | A normal invoice email with a PDF attachment stays low risk. |
| `suspicious_html_notice.eml` | Suspicious | `CRITICAL` | Strong domain, authentication, and social-engineering signals align with a clearly malicious posture. |
| `suspicious_password_reset_portal.eml` | Suspicious | `HIGH` or `CRITICAL` | Shortener, suspicious TLD, failed authentication, and credential request remain clearly suspicious. |
| `suspicious_shortener_login_notice.eml` | Suspicious | Suspicious, non-critical | Useful for observing shortener plus credential-request behavior without relying on auth failure. |
| `suspicious_lookalike_domain_notice.eml` | Suspicious | Suspicious, non-critical | Isolates lookalike-domain risk with otherwise passing authentication. |
| `suspicious_invoice_payment_followup.eml` | Suspicious | `HIGH` or `CRITICAL` | Executable attachment and financial pressure remain strong high-risk signals. |

---

## Confirmed Calibration Outcome

### Credential request term refinement

The first clear false positive found during calibration was:

```text
benign_password_reset_notice.eml
```

It originally triggered:

```text
SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS
```

because the configuration treated the generic term:

```text
password
```

as a credential-request signal.

The refined configuration now uses more explicit phrases:

```text
confirm your login
confirm your password
enter your password
verify your account
```

This keeps explicit phishing-style credential requests suspicious while allowing benign password reset notices to remain low risk.

---

## Current Observations

- Broad keyword-only social-engineering terms can create false positives faster than scoring weights do.
- Narrowing detection phrases is sometimes a better first move than lowering weights globally.
- Suspicious shortener and lookalike-domain emails are useful calibration cases because they test subtle threat posture without depending on authentication failure.
- Executable attachments remain one of the strongest and most reliable critical indicators in the current MVP.

---

## Next Candidate Questions

The next scoring review should focus on these questions:

1. Should shortener plus explicit credential-request wording remain non-critical, or should it score higher?
2. Should an isolated lookalike domain remain non-critical, or should its current weight increase?
3. Do we need more benign security or identity-related fixtures before changing weights again?
4. Are there legitimate billing or account-support cases that still look too suspicious under the current terms?

Until those questions are backed by fixture evidence, keep the current weights unchanged.
