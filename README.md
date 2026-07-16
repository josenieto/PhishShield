# PhishShield

Local, self-hosted phishing email analysis toolkit.

## Current MVP

The current MVP provides a local `.eml` analysis flow with:

- FastAPI backend analysis for uploaded email messages;
- React + TypeScript + Vite frontend upload and result inspection flow;
- extracted evidence rendering for sender, subject, URLs, attachment names, and authentication results;
- grouped findings with backend-provided severity and explanation text;
- frontend-side Markdown report download for the current analysis result;
- backend Docker runtime and Compose wiring;
- CI coverage for backend tests, frontend tests/build, and backend Docker smoke;
- coverage reporting in observability mode for backend and frontend.

## Development

### Install

```bash
python -m pip install -e ".[test]"
```

### Run Tests

```bash
python -m pytest
```

### Run Backend Coverage

Coverage is currently observational only. No CI gate or minimum threshold is enforced yet.

```bash
python -m pytest --cov=src --cov-report=term-missing
```

### Run Frontend Tests

```bash
cd frontend
npm run test
npm run build
```

### Run Frontend Coverage

Coverage is currently observational only. No CI gate or minimum threshold is enforced yet.

```bash
cd frontend
npm run test:coverage
```

### Run API

```bash
python -m uvicorn infrastructure.entrypoints.api.app:create_app --factory --reload
```

### Run Frontend

The frontend lives in `frontend/` and uses Vite's development proxy to call the backend through `/api`.

Start the backend first:

```bash
python -m uvicorn infrastructure.entrypoints.api.app:create_app --factory --reload
```

Then start the frontend:

```bash
cd frontend
npm install
npm run dev
```

The frontend development server proxies:

```text
/api -> http://127.0.0.1:8000
```

Open the URL printed by Vite, usually:

```text
http://127.0.0.1:5173
```

On Windows PowerShell environments that block `npm.ps1`, use:

```powershell
cmd /c npm install
cmd /c npm run dev
```

### Run With Docker

Build and run the backend with Docker Compose:

```bash
docker compose up --build
```

The Compose file forwards:

- `8000:8000`
- `PHISHSHIELD_MAX_UPLOAD_BYTES` from the shell or Compose environment

Health check example:

```bash
curl http://127.0.0.1:8000/health
```

Analyze email example:

```bash
curl -X POST http://127.0.0.1:8000/analyze-email -F "file=@tests/fixtures/emails/suspicious_html_notice.eml;type=message/rfc822"
```

### Runtime Configuration

The API reads runtime settings from environment variables when the app is created.

`.env.example` documents the currently supported runtime variables. Export them in your shell or provide them through your runtime environment.

Available variables:

| Variable | Default | Description |
|---|---:|---|
| `PHISHSHIELD_MAX_UPLOAD_BYTES` | `1_000_000` | Maximum accepted `.eml` upload size in bytes. Must be a positive integer. |

POSIX example:

```bash
PHISHSHIELD_MAX_UPLOAD_BYTES=2000000 python -m uvicorn infrastructure.entrypoints.api.app:create_app --factory --reload
```

PowerShell example:

```powershell
$env:PHISHSHIELD_MAX_UPLOAD_BYTES = "2000000"
python -m uvicorn infrastructure.entrypoints.api.app:create_app --factory --reload
```

### Documentation

- API contract: `doc/API.md`
- Backend roadmap: `doc/BACKEND_EVOLUTION_PLAN.md`
- Frontend MVP plan: `doc/FRONTEND_MVP_PLAN.md`
- Scoring calibration baseline: `doc/SCORING_CALIBRATION.md`

The current recommended next group after the initial Markdown report export is additional runtime validation on an environment with Docker available or a frontend workbench layout redesign.

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

### Analyze Email

```bash
curl -X POST http://127.0.0.1:8000/analyze-email -F "file=@sample.eml;type=message/rfc822"
```

See `doc/API.md` for the full request and response contract, error behavior, and current integration-test coverage examples.
