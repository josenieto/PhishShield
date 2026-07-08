# PhishShield

Local, self-hosted phishing email analysis toolkit.

## Backend Development

### Install

```bash
python -m pip install -e ".[test]"
```

### Run Tests

```bash
python -m pytest
```

### Run API

```bash
python -m uvicorn infrastructure.entrypoints.api.app:create_app --factory --reload
```

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

### Analyze Email

```bash
curl -X POST http://127.0.0.1:8000/analyze-email -F "file=@sample.eml;type=message/rfc822"
```

Request notes:

- field name: `file`
- expected content type: `message/rfc822`
- current default upload limit: `1_000_000` bytes

Successful responses return a JSON body with:

- `finding_codes`: emitted finding codes, including repeated evidence when applicable;
- `unique_finding_codes`: deduplicated finding codes;
- `finding_summary`: categorized finding metadata and highest severity;
- `risk_score`: weighted score, capped score, risk level, and critical-indicator flag.

Example response shape:

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
  }
}
```

Current API behavior:

- oversized uploads return `413` with `{"detail": "Uploaded email exceeds maximum allowed size."}`;
- unexpected analysis failures return `422` with `{"detail": "Uploaded email could not be analyzed."}`;
- malformed but parseable emails degrade to a controlled low-information response instead of failing the request.
