# API Contract

## Endpoints

- `GET /health`
- `POST /analyze-email`

---

## `GET /health`

Returns a basic health response:

```json
{"status": "ok"}
```

---

## `POST /analyze-email`

Analyzes an uploaded `.eml` email message and returns findings plus a risk summary.

### Request

Expected multipart field:

- field name: `file`
- expected content type: `message/rfc822`
- default upload limit: `1_000_000` bytes, configurable with `PHISHSHIELD_MAX_UPLOAD_BYTES`

Example:

```bash
curl -X POST http://127.0.0.1:8000/analyze-email -F "file=@sample.eml;type=message/rfc822"
```

### Response Shape

Successful responses return a JSON body with:

- `finding_codes`: emitted finding codes, including repeated evidence when applicable;
- `unique_finding_codes`: deduplicated finding codes;
- `finding_summary`: categorized finding metadata and highest severity;
- `risk_score`: weighted score, capped score, risk level, and critical-indicator flag.
- `extracted_evidence`: normalized sender, subject, URLs, attachment filenames, and extracted authentication results.

Current response model fields:

- `finding_codes: list[str]`
- `unique_finding_codes: list[str]`
- `finding_summary.findings: list[{code, category, severity}]`
- `finding_summary.sorted_findings: list[{code, category, severity}]`
- `finding_summary.finding_counts_by_category: dict[str, int]`
- `finding_summary.highest_severity: str`
- `finding_summary.total_findings: int`
- `risk_score.indicators: list[str]`
- `risk_score.raw_score: int`
- `risk_score.capped_score: int`
- `risk_score.risk_level: str`
- `risk_score.has_critical_indicators: bool`
- `extracted_evidence.sender_domain: str`
- `extracted_evidence.subject: str`
- `extracted_evidence.urls: list[str]`
- `extracted_evidence.attachment_filenames: list[str]`
- `extracted_evidence.authentication_results.spf_result: str`
- `extracted_evidence.authentication_results.dkim_result: str`
- `extracted_evidence.authentication_results.dmarc_result: str`

### Example Response

```json
{
  "finding_codes": [
    "DOMAIN_HAS_SUSPICIOUS_TLD",
    "AUTHENTICATION_SPF_FAILED",
    "AUTHENTICATION_DMARC_FAILED",
    "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS",
    "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS"
  ],
  "unique_finding_codes": [
    "DOMAIN_HAS_SUSPICIOUS_TLD",
    "AUTHENTICATION_SPF_FAILED",
    "AUTHENTICATION_DMARC_FAILED",
    "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS",
    "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS"
  ],
  "finding_summary": {
    "findings": [
      {
        "code": "DOMAIN_HAS_SUSPICIOUS_TLD",
        "category": "DOMAIN",
        "severity": "HIGH"
      },
      {
        "code": "AUTHENTICATION_DMARC_FAILED",
        "category": "AUTHENTICATION",
        "severity": "CRITICAL"
      }
    ],
    "sorted_findings": [
      {
        "code": "AUTHENTICATION_DMARC_FAILED",
        "category": "AUTHENTICATION",
        "severity": "CRITICAL"
      },
      {
        "code": "DOMAIN_HAS_SUSPICIOUS_TLD",
        "category": "DOMAIN",
        "severity": "HIGH"
      }
    ],
    "finding_counts_by_category": {
      "AUTHENTICATION": 2,
      "DOMAIN": 1,
      "SOCIAL_ENGINEERING": 2
    },
    "highest_severity": "CRITICAL",
    "total_findings": 5
  },
  "risk_score": {
    "indicators": [
      "DOMAIN_HAS_SUSPICIOUS_TLD",
      "AUTHENTICATION_SPF_FAILED",
      "AUTHENTICATION_DMARC_FAILED",
      "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS",
      "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS"
    ],
    "raw_score": 130,
    "capped_score": 100,
    "risk_level": "CRITICAL",
    "has_critical_indicators": true
  },
  "extracted_evidence": {
    "sender_domain": "example.zip",
    "subject": "Urgent account notice",
    "urls": [
      "https://example.com/login"
    ],
    "attachment_filenames": [],
    "authentication_results": {
      "spf_result": "fail",
      "dkim_result": "pass",
      "dmarc_result": "fail"
    }
  }
}
```

### Error Behavior

- oversized uploads return `413` with `{"detail": "Uploaded email exceeds maximum allowed size."}`;
- unexpected analysis failures return `422` with `{"detail": "Uploaded email could not be analyzed."}`;
- malformed but parseable emails degrade to a controlled low-information response instead of failing the request.

### Contract Examples Covered By Integration Tests

- suspicious upload -> `200` with findings and critical risk;
- benign upload -> `200` with no findings and low risk;
- suspicious attachment upload -> `200` with attachment findings;
- malformed but parseable upload -> `200` with controlled fallback findings;
- oversized upload -> `413` with stable error payload;
- unexpected analyzer failure -> `422` with stable error payload.
