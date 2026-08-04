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
