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
