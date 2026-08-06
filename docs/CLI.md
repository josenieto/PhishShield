# Deterministic CLI

## Command

```text
phishshield analyze path/to/email.eml [--format text|json] [--fail-on none|low|medium|high|critical]
```

The command analyzes one `.eml` file through the same deterministic application
use case used by the API. It does not start FastAPI, require Docker, or invoke
the optional model-assisted branch.

## Output

The default `text` format prints risk level, capped score, subject, sender
domain, finding count, and sorted findings. The `json` format emits the
deterministic API response shape and is suitable for scripts.

## Exit Codes

```text
0  analysis completed and --fail-on threshold was not reached
1  analysis completed and --fail-on threshold was reached
2  usage or argument error
3  input file is missing or unreadable
4  email is invalid, oversized, or analysis failed
```

## Examples

PowerShell:

```powershell
phishshield analyze .\sample.eml --format json
if ($LASTEXITCODE -eq 1) { Write-Host "Risk threshold reached" }
```

Bash:

```bash
phishshield analyze ./sample.eml --fail-on high
```

CI:

```yaml
- name: Analyze email
  run: phishshield analyze artifacts/sample.eml --format json --fail-on high
```

The deterministic result is triage evidence, not a malware verdict. The
advisory model remains optional, disabled by default, and is not a default CI
gate.

## GitHub Actions Artifact Workflow

The reusable workflow at
`.github/workflows/deterministic-email-artifact.yml` analyzes an artifact
containing exactly one `.eml` file and uploads the JSON report as
`deterministic-email-analysis`.

The calling workflow must upload the email artifact first, then invoke the
reusable workflow:

```yaml
jobs:
  upload-email:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/upload-artifact@v4
        with:
          name: email-under-analysis
          path: artifacts/sample.eml

  analyze-email:
    needs: upload-email
    uses: OWNER/REPOSITORY/.github/workflows/deterministic-email-artifact.yml@integration/master
    with:
      email-artifact: email-under-analysis
      fail-on: high
      report-retention-days: 7
```

This repository also contains a manual smoke caller at
`.github/workflows/deterministic-email-artifact-smoke.yml`. Run it from the
GitHub Actions tab to validate artifact upload, reusable-workflow invocation,
JSON report publication, and threshold handling. Select `benign` to expect a
green run, or select `suspicious` with `fail-on: high` to expect the report to
be published before the job fails intentionally. The smoke workflow uses
one-day report retention and contains no production email.

The workflow accepts exit code `1` from the CLI as a completed analysis whose
risk threshold was reached. It uploads the JSON report first and then fails the
job intentionally. Input email contents and generated reports remain workflow
artifacts and are not committed to Git. Set a short retention period and apply
your organization's access controls when emails contain sensitive information.
