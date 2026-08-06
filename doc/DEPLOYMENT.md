# Local Deployment

## Prerequisites

- Docker Engine with Compose support;
- a host port available for the frontend, `8080` by default.

## Start The MVP

From the repository root:

```bash
docker compose up --build
```

Open the Web UI at:

```text
http://localhost:8080
```

The Compose stack builds a production frontend image with Nginx Alpine and a
backend image with the deterministic FastAPI API. The frontend is the only
service published to the host. API requests are proxied internally through
`/api`.

## Health Check

Check the backend through the frontend proxy:

```bash
curl http://localhost:8080/api/health
```

Expected response:

```json
{"status":"ok"}
```

The backend is not published on `localhost:8000` by the product Compose file.

## Runtime Configuration

Copy `.env.example` to `.env` when configuration is needed. Supported values:

```text
PHISHSHIELD_FRONTEND_PORT=8080
PHISHSHIELD_MAX_UPLOAD_BYTES=1000000
PHISHSHIELD_MODEL_ASSESSMENT_ENABLED=false
```

The advisory model remains disabled in Compose by default. Do not enable it for
the public or shared deployment profile without reviewing its experimental
status and configuring external artifact paths explicitly.

To use another frontend host port:

```text
PHISHSHIELD_FRONTEND_PORT=9090
```

Then restart the stack and open `http://localhost:9090`.

## Logs And Shutdown

Follow logs:

```bash
docker compose logs -f
```

Stop the stack:

```bash
docker compose down
```

Rebuild after source or dependency changes:

```bash
docker compose up --build
```

## Privacy And Exposure

This deployment is intended for local use or a trusted internal network. It
does not provide authentication, persistence, email history, HTTPS, rate
limiting, or multi-user access control.

- Do not upload confidential, personal, or production email to an untrusted host.
- Do not expose the stack directly to the public Internet.
- Do not execute attachments or follow links from analyzed messages.
- Review reverse-proxy, HTTPS, access-control, logging, and retention policies
  before any shared deployment.
- The application processes uploaded messages without a persistence database.

## Native Development

The Compose deployment is the simplest product path. Native development remains
available when iterating on the backend and frontend separately. See
`README.md`, `doc/CLI.md`, and `doc/API.md` for those workflows.
