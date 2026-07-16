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
| `benign_shipping_delivery_update.eml` | Benign | `LOW` | A routine shipping notification with a legitimate tracking link stays low risk. |
| `benign_cloud_document_share_notice.eml` | Benign | `LOW` | A normal collaboration share notice stays low risk despite document-sharing wording and a normal HTTPS link. |
| `benign_billing_payment_receipt.eml` | Benign | `LOW` | A standard billing receipt with a legitimate receipt link stays clean under the current financial-pressure terms. |
| `benign_hr_policy_update.eml` | Benign | `LOW` | A normal internal HR policy update remains low risk despite policy-review wording and a normal HTTPS link. |
| `suspicious_html_notice.eml` | Suspicious | `CRITICAL` | Strong domain, authentication, and social-engineering signals align with a clearly malicious posture. |
| `suspicious_password_reset_portal.eml` | Suspicious | `HIGH` or `CRITICAL` | Shortener, suspicious TLD, failed authentication, and credential request remain clearly suspicious. |
| `suspicious_cloud_document_share_lure.eml` | Suspicious | `MEDIUM`, non-critical | A shortener plus account-verification wording lands at `raw_score=40`, making the lure visible without treating it like a confirmed compromise on its own. |
| `suspicious_qr_login_lure.eml` | Suspicious | `MEDIUM`, non-critical | A QR-themed login lure remains visible through the current shortener plus account-verification signals without introducing QR-specific parsing. |
| `suspicious_shortener_login_notice.eml` | Suspicious | `MEDIUM`, non-critical | Shortener plus explicit login confirmation wording currently lands at `raw_score=40`, which is visible without being over-escalated. |
| `suspicious_mfa_reverification_notice.eml` | Suspicious | `HIGH`, non-critical | A lookalike Punycode domain plus account-verification wording lands at `raw_score=55`, which is appropriately elevated without relying on authentication failure. |
| `suspicious_lookalike_domain_notice.eml` | Suspicious | `MEDIUM`, non-critical | An isolated Punycode/lookalike domain currently lands at `raw_score=30`, which keeps the signal visible without treating it as critical alone. |
| `suspicious_invoice_link_payment_lure.eml` | Suspicious | `MEDIUM`, non-critical | An attachment-free invoice lure with financial-pressure wording and a shortener stays visible at `raw_score=30` without needing executable content. |
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
- Benign shipping and document-sharing notifications currently stay clean under the narrowed social-engineering phrases, which is a good sign for common business email traffic.
- Benign billing receipts and HR policy notices also stay clean, which broadens confidence in ordinary operational email traffic.
- A shortener plus account-verification wording remains a useful medium-risk lure baseline even when authentication passes.
- QR-themed phishing can already be surfaced through existing shortener and credential-request signals, even before any QR-specific parsing exists.
- Attachment-free invoice-payment lures remain visible at medium risk when they combine shortener and financial-pressure wording.
- A lookalike Punycode domain combined with account-verification wording now provides a stable high-risk, non-critical calibration case without needing failed authentication.
- Executable attachments remain one of the strongest and most reliable critical indicators in the current MVP.
- The current scoring weights already place shortener-plus-credential and isolated lookalike-domain cases in `MEDIUM`, which is acceptable for the current MVP baseline.

---

## Next Candidate Questions

The next scoring review should focus on these questions:

1. Do we need QR-themed or invoice-link-specific text signals beyond the current shortener and credential/financial baselines?
2. Are there legitimate billing or account-support cases that still look too suspicious under the current terms?
3. Should subtle suspicious cases move above `MEDIUM` only when an additional supporting signal appears?
4. Are current critical indicators still reserved for the strongest combinations of evidence?

Until those questions are backed by fixture evidence, keep the current weights unchanged.
