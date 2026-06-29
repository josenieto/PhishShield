# Domain Pure Functions Plan

## Purpose

This document defines an incremental technical backlog of candidate pure functions for the PhishShield `domain` layer.

It is not a plan to implement everything at once.  
Its purpose is to preserve context, group related functions, and support controlled progress:

```text
pure domain function
        ↓
unit test
        ↓
possible value object / entity
        ↓
Application use case, if applicable
        ↓
Infrastructure port / adapter, if applicable
        ↓
entrypoint/API, if applicable
```

Each functional group must be developed independently, with small and verifiable commits.

---

## Domain purity principles

A function can live in `src/domain/` if it satisfies these conditions:

- it receives primitive values or domain models;
- it returns primitive values or domain models;
- it performs no IO;
- it does not read or write files;
- it does not call the network;
- it does not query DNS;
- it does not use FastAPI;
- it does not use Playwright;
- it does not use Ollama;
- it does not use YARA;
- it does not use Tesseract/OCR;
- it does not use external PDF, Office, or `.eml` parsers;
- it does not depend on environment variables;
- it does not depend on mutable global configuration;
- it always returns the same output for the same input;
- it can be tested with Pytest without complex mocks.

If a function needs network access, filesystem access, external processes, SDKs, a browser, AI, OCR, YARA, or parsing libraries, it does not belong directly in `domain`. It belongs in `infrastructure` behind a port defined in `application`.

---

## Workflow per group

For each functional group:

1. Select one function or a very small subgroup.
2. Define the contract:
   - name,
   - signature,
   - inputs,
   - expected output,
   - edge cases.
3. Create unit tests.
4. Implement the pure function.
5. Run tests.
6. Check whether a real need appears for:
   - value object,
   - entity,
   - enum,
   - domain error.
7. Only then decide whether to move upward:
   - `application/use_cases`,
   - `application/ports`,
   - `infrastructure/adapters`,
   - `infrastructure/entrypoints/api`.
8. Make a small commit.

---

## General status

| Group | Status | Priority |
|---|---:|---:|
| Text normalization | Done | High |
| Homoglyphs / suspicious Unicode | Done | High |
| Domain analysis | Done | High |
| URL analysis | Done | High |
| Attachment analysis | Done | High |
| Authentication result analysis | Done | Medium |
| Risk scoring | Done | High |
| Social engineering heuristics | Done | Medium |
| Finding analysis | Done | Medium |
| Hash analysis | Done | Medium |

---

# 1. Text normalization

## Purpose

Pure functions for normalizing text before applying analysis rules.  
They are useful for subjects, visible sender names, visual domains, body text, OCR-extracted text, and filenames.

## Suggested location

```text
src/domain/services/text_normalization/
```

## Candidate functions

### `normalize_whitespace`

```python
normalize_whitespace(text: str) -> str
```

Normalizes repeated spaces, tabs, and line breaks.

Expected behavior:

- collapses consecutive spaces;
- trims leading/trailing spaces;
- preserves meaningful textual content.

Suggested tests:

- text with multiple spaces;
- text with tabs;
- text with repeated line breaks;
- empty string;
- already normalized string.

---

### `normalize_unicode_text`

```python
normalize_unicode_text(text: str) -> str
```

Applies standard Unicode normalization using the Python standard library, for example `unicodedata`.

Expected behavior:

- normalizes equivalent Unicode forms;
- keeps readable text;
- does not remove characters by itself.

Suggested tests:

- composed characters;
- decomposed characters;
- ASCII text;
- text with accents;
- empty string.

---

### `strip_invisible_chars`

```python
strip_invisible_chars(text: str) -> str
```

Removes invisible or control characters that may hide malicious content.

Expected behavior:

- removes zero-width spaces;
- removes non-printable control characters;
- preserves visible text.

Suggested tests:

- text with `\u200b`;
- text with `\u200c`;
- text with control characters;
- text without invisible characters;
- empty string.

---

### `contains_invisible_chars`

```python
contains_invisible_chars(text: str) -> bool
```

Detects whether text contains suspicious invisible characters.

Expected behavior:

- returns `True` when invisible characters are present;
- returns `False` for normal text.

Suggested tests:

- text with zero-width space;
- text with control characters;
- clean text;
- empty string.

## Outside the domain

This group must not:

- read files;
- parse `.eml`;
- run OCR;
- call external libraries;
- modify file encodings on disk.

## Possible next layer

After this group is complete:

- `application` may use these functions inside a text analysis use case;
- `infrastructure` may provide extracted text from `.eml`, OCR, PDF, or Office sources.

---

# 2. Homoglyphs / suspicious Unicode

## Purpose

Detect pure signals of suspicious Unicode, mixed scripts, and visually confusable characters.

This group is critical for detecting homoglyph attacks in domains, sender names, subjects, and visible text.

## Suggested location

```text
src/domain/services/homoglyphs/
```

## Candidate functions

### `detect_unicode_scripts`

```python
detect_unicode_scripts(text: str) -> set[str]
```

Detects Unicode scripts present in text.

Example outputs:

```text
{"LATIN"}
{"LATIN", "CYRILLIC"}
{"GREEK"}
```

Suggested tests:

- Latin text;
- Cyrillic text;
- Greek text;
- mixed Latin/Cyrillic text;
- numbers and symbols;
- empty string.

---

### `contains_mixed_scripts`

```python
contains_mixed_scripts(text: str) -> bool
```

Detects suspicious alphabet mixing.

Expected behavior:

- `False` for normal Latin text;
- `True` for Latin + Cyrillic mixtures;
- numbers and punctuation should be treated as neutral.

Suggested tests:

- normal `microsoft.com`;
- domain with a Cyrillic `о`;
- text with numbers;
- text with hyphens;
- empty string.

---

### `contains_confusable_characters`

```python
contains_confusable_characters(text: str) -> bool
```

Detects potentially confusable characters using a minimal internal table.

Expected behavior:

- detects visually similar characters;
- does not depend on external libraries;
- does not perform full IDNA conversion.

Suggested tests:

- Cyrillic letters similar to Latin letters;
- Greek letters similar to Latin letters;
- clean text;
- empty string.

---

### `find_confusable_characters`

```python
find_confusable_characters(text: str) -> list[str]
```

Returns suspicious characters found in text.

Expected behavior:

- preserves discovery order;
- may return duplicates or unique values depending on the final contract;
- returns an empty list when there are no findings.

Suggested tests:

- one confusable character;
- multiple confusable characters;
- repeated characters;
- clean text.

## Outside the domain

This group must not:

- resolve domains;
- query external lists;
- call reputation services;
- perform HTTP requests;
- use external threat intelligence libraries.

## Possible next layer

After this group is complete:

- `application` may create a use case for analyzing extracted domains;
- `infrastructure` may provide domains from `.eml`, PDF, or HTML parsers.

---

# 3. Domain analysis

## Purpose

Pure functions for analyzing structural properties of domains and hosts.

## Suggested location

```text
src/domain/services/domain_analysis/
```

## Candidate functions

### `split_domain_labels`

```python
split_domain_labels(domain: str) -> list[str]
```

Splits a domain into labels.

Example:

```text
login.example.com -> ["login", "example", "com"]
```

Suggested tests:

- simple domain;
- subdomain;
- domain with trailing dot;
- empty domain;
- domain with spaces.

---

### `is_punycode_label`

```python
is_punycode_label(label: str) -> bool
```

Detects whether a label starts with `xn--`.

Suggested tests:

- `xn--example`;
- `example`;
- upper/lowercase;
- empty string.

---

### `contains_punycode`

```python
contains_punycode(domain: str) -> bool
```

Detects whether a domain contains any Punycode label.

Suggested tests:

- domain with `xn--`;
- domain without Punycode;
- subdomain with Punycode;
- empty string.

---

### `has_suspicious_subdomain_depth`

```python
has_suspicious_subdomain_depth(domain: str, max_depth: int = 4) -> bool
```

Detects suspiciously deep subdomain structures.

Suggested tests:

- domain with few labels;
- domain with many subdomains;
- boundary value;
- custom `max_depth`.

---

### `looks_like_ip_address_host`

```python
looks_like_ip_address_host(host: str) -> bool
```

Detects whether a host looks like an IP address instead of a domain.

Suggested tests:

- valid IPv4;
- IPv4-like invalid text;
- normal domain;
- empty host.

---

### `has_suspicious_tld`

```python
has_suspicious_tld(domain: str, suspicious_tlds: set[str]) -> bool
```

Evaluates risky TLDs using a set passed as an argument.

Expected behavior:

- does not read global configuration;
- does not query external lists;
- works only with provided data.

Suggested tests:

- domain with suspicious TLD;
- domain with normal TLD;
- empty list;
- upper/lowercase.

## Outside the domain

This group must not:

- resolve DNS;
- query WHOIS;
- call reputation APIs;
- download TLD lists.

## Possible next layer

After this group is complete:

- `application` may orchestrate domain analysis;
- `infrastructure` may resolve redirects or enrich reputation.

---

# 4. URL analysis

## Purpose

Pure functions for classifying URLs or already parsed URL components.

## Suggested location

```text
src/domain/services/url_analysis/
```

## Candidate functions

### `is_url_scheme_allowed`

```python
is_url_scheme_allowed(scheme: str, allowed_schemes: set[str]) -> bool
```

Checks whether the scheme is allowed.

Suggested tests:

- `http`;
- `https`;
- `mailto`;
- uppercase;
- empty scheme.

---

### `is_suspicious_url_scheme`

```python
is_suspicious_url_scheme(scheme: str) -> bool
```

Detects suspicious schemes such as:

```text
javascript
data
file
vbscript
```

Suggested tests:

- `javascript`;
- `data`;
- `file`;
- `https`;
- upper/lowercase.

---

### `has_embedded_credentials`

```python
has_embedded_credentials(url: str) -> bool
```

Detects URLs with embedded credentials.

Example:

```text
https://user:pass@example.com
```

Suggested tests:

- URL with user;
- URL with user and password;
- normal URL;
- malformed URL.

---

### `has_suspicious_query_density`

```python
has_suspicious_query_density(url: str, threshold: int) -> bool
```

Detects dense query strings or too many query parameters.

Suggested tests:

- URL without query;
- URL with few parameters;
- URL with many parameters;
- custom threshold.

---

### `has_url_shortener_domain`

```python
has_url_shortener_domain(domain: str, known_shorteners: set[str]) -> bool
```

Detects known shorteners using a set passed as an argument.

Suggested tests:

- shortener domain;
- non-shortener domain;
- empty set;
- upper/lowercase.

## Outside the domain

This group must not:

- perform HEAD requests;
- perform GET requests;
- follow redirects;
- open a browser;
- query reputation services.

## Possible next layer

After this group is complete:

- `application` may define a `LinkAnalyzerPort`;
- `infrastructure` may implement passive HTTP resolution.

---

# 5. Attachment analysis

## Purpose

Pure functions for classifying attachments from available metadata, especially filename and extension.

## Suggested location

```text
src/domain/services/attachment_analysis/
```

## Candidate functions

### `is_executable_extension`

```python
is_executable_extension(filename: str) -> bool
```

Detects executable extensions such as:

```text
.exe
.bat
.cmd
.scr
.ps1
.vbs
.js
.jar
```

Suggested tests:

- `.exe`;
- `.pdf`;
- uppercase;
- file without extension;
- double extension.

---

### `is_office_document_extension`

```python
is_office_document_extension(filename: str) -> bool
```

Detects Office documents, especially macro-enabled formats.

Examples:

```text
.doc
.docx
.docm
.xls
.xlsx
.xlsm
.ppt
.pptx
.pptm
```

Suggested tests:

- `.docx`;
- `.docm`;
- `.xlsm`;
- `.pdf`;
- uppercase.

---

### `is_pdf_extension`

```python
is_pdf_extension(filename: str) -> bool
```

Detects PDF files by extension.

Suggested tests:

- `.pdf`;
- `.PDF`;
- `invoice.pdf.exe`;
- no extension.

---

### `has_double_extension`

```python
has_double_extension(filename: str) -> bool
```

Detects patterns such as:

```text
invoice.pdf.exe
document.docx.scr
```

Suggested tests:

- dangerous double extension;
- non-dangerous double extension;
- single extension;
- filename without extension.

---

### `has_suspicious_filename_chars`

```python
has_suspicious_filename_chars(filename: str) -> bool
```

Detects invisible characters, unusual separators, or suspicious Unicode.

Suggested tests:

- filename with zero-width space;
- filename with control characters;
- normal filename;
- filename with mixed Unicode.

---

### `classify_attachment_extension`

```python
classify_attachment_extension(filename: str) -> str
```

Classifies attachments into categories.

Candidate categories:

```text
PDF
OFFICE
EXECUTABLE
IMAGE
ARCHIVE
TEXT
UNKNOWN
```

Suggested tests:

- PDF;
- macro-enabled Office document;
- executable;
- image;
- archive;
- unknown.

## Outside the domain

This group must not:

- open files;
- read bytes;
- calculate hashes from disk;
- extract macros;
- analyze real PDFs;
- run YARA.

## Possible next layer

After this group is complete:

- `application` may orchestrate attachment scanning;
- `infrastructure` may implement PDF, Office, YARA, and real hash adapters.

---

# 6. Authentication result analysis

## Purpose

Interpret already computed SPF, DKIM, and DMARC results.

The domain must not query DNS or validate cryptographic signatures.  
It may only classify results already calculated by infrastructure.

## Suggested location

```text
src/domain/services/authentication_analysis/
```

## Candidate functions

### `is_authentication_aligned`

```python
is_authentication_aligned(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> bool
```

Evaluates whether authentication results are aligned.

Suggested tests:

- all `pass`;
- SPF fail, DKIM pass, DMARC pass;
- DMARC fail;
- unknown values.

---

### `classify_authentication_risk`

```python
classify_authentication_risk(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> str
```

Classifies authentication risk.

Candidate categories:

```text
LOW
MEDIUM
HIGH
CRITICAL
UNKNOWN
```

Suggested tests:

- all pass;
- SPF fail;
- DKIM fail;
- DMARC fail;
- multiple failures;
- missing values.

---

### `has_authentication_failure`

```python
has_authentication_failure(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> bool
```

Detects whether a relevant authentication failure exists.

Suggested tests:

- all pass;
- one failure;
- several failures;
- neutral/none;
- unknown.

---

### `summarize_authentication_findings`

```python
summarize_authentication_findings(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> list[str]
```

Returns textual findings or finding codes.

Suggested tests:

- SPF fail;
- DKIM fail;
- DMARC fail;
- all pass;
- unknown results.

## Outside the domain

This group must not:

- query DNS;
- cryptographically validate DKIM;
- parse raw headers;
- call external authentication libraries.

## Possible next layer

After this group is complete:

- `application` may orchestrate identity analysis;
- `infrastructure` may parse headers and calculate SPF/DKIM/DMARC results.

---

# 7. Risk scoring

## Purpose

Pure functions for converting indicators into scores and risk levels.

## Suggested location

```text
src/domain/services/risk_scoring/
```

## Candidate functions

### `calculate_indicator_score`

```python
calculate_indicator_score(
    indicators: list[str],
    weights: dict[str, int],
) -> int
```

Sums weights associated with indicators.

Suggested tests:

- known indicators;
- unknown indicators;
- empty list;
- negative weights if allowed or rejected;
- duplicates.

---

### `classify_risk_level`

```python
classify_risk_level(score: int) -> str
```

Converts a score into a risk level.

Candidate categories:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Suggested tests:

- exact thresholds;
- low;
- medium;
- high;
- critical;
- negative score.

---

### `combine_risk_scores`

```python
combine_risk_scores(scores: list[int]) -> int
```

Combines partial scores.

Suggested tests:

- empty list;
- multiple values;
- negative values;
- extreme values.

---

### `cap_risk_score`

```python
cap_risk_score(
    score: int,
    min_score: int = 0,
    max_score: int = 100,
) -> int
```

Caps a score to a range.

Suggested tests:

- score below minimum;
- score above maximum;
- score inside range;
- custom limits.

---

### `has_critical_indicators`

```python
has_critical_indicators(
    indicators: list[str],
    critical_indicators: set[str],
) -> bool
```

Detects whether any critical indicator is present.

Suggested tests:

- critical indicator present;
- no critical indicator;
- empty list;
- empty critical set.

## Outside the domain

This group must not:

- call AI;
- query external reputation;
- depend on global configuration weights;
- generate API reports.

## Possible next layer

After this group is complete:

- `application` may compose module results;
- `infrastructure` may provide findings from parsers and adapters.

---

# 8. Social engineering heuristics

## Purpose

Simple deterministic text heuristics for detecting social engineering signals.

Local AI may complement this analysis, but it must not replace these pure rules.

## Suggested location

```text
src/domain/services/social_engineering/
```

## Candidate functions

### `contains_urgency_terms`

```python
contains_urgency_terms(text: str, terms: set[str]) -> bool
```

Detects urgency terms.

Suggested tests:

- text with urgency term;
- text without term;
- upper/lowercase;
- empty terms set.

---

### `contains_financial_pressure_terms`

```python
contains_financial_pressure_terms(text: str, terms: set[str]) -> bool
```

Detects financial pressure.

Suggested tests:

- urgent invoice;
- account lock;
- neutral text;
- empty terms.

---

### `contains_credential_request_terms`

```python
contains_credential_request_terms(text: str, terms: set[str]) -> bool
```

Detects credential request wording.

Suggested tests:

- `password`;
- `verify your account`;
- neutral text;
- upper/lowercase.

---

### `count_social_engineering_signals`

```python
count_social_engineering_signals(
    text: str,
    signal_terms: dict[str, set[str]],
) -> dict[str, int]
```

Counts signals by category.

Suggested tests:

- one category;
- multiple categories;
- no signals;
- empty text.

---

### `classify_social_engineering_risk`

```python
classify_social_engineering_risk(
    signal_counts: dict[str, int],
) -> str
```

Classifies risk from signal counts.

Candidate categories:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Suggested tests:

- no signals;
- few signals;
- multiple signals;
- critical signals.

## Outside the domain

This group must not:

- call Ollama;
- perform external NLP;
- use ML models;
- read prompts;
- depend on global configuration.

## Possible next layer

After this group is complete:

- `application` may combine heuristics with technical findings;
- `infrastructure` may use Ollama as complementary analysis.

---

# 9. Finding analysis

## Purpose

Pure functions for composing, filtering, and ordering findings.

Later, these functions should operate on value objects or entities such as `Finding`, `RiskIndicator`, or `AnalysisResult`.

## Suggested location

```text
src/domain/services/finding_analysis/
```

## Candidate functions

### `deduplicate_finding_codes`

```python
deduplicate_finding_codes(finding_codes: list[str]) -> list[str]
```

Removes duplicate finding codes while preserving first occurrence order.

Suggested tests:

- list with duplicates;
- list without duplicates;
- empty list;
- order preservation.

---

### `sort_findings_by_severity`

```python
sort_findings_by_severity(findings: list[Finding]) -> list[Finding]
```

Sorts findings by severity.

Current severity order:

```text
CRITICAL
HIGH
MEDIUM
LOW
UNKNOWN
```

Unrecognized severities are treated as `UNKNOWN`, and sorting preserves input order for findings with the same severity.

Suggested tests:

- mixed severities;
- unknown severity;
- empty list;
- stable ordering.

---

### `filter_findings_by_category`

```python
filter_findings_by_category(
    findings: list[Finding],
    category: str,
) -> list[Finding]
```

Filters findings by category.

Suggested tests:

- existing category;
- missing category;
- empty list;
- category casing.

---

### `count_findings_by_category`

```python
count_findings_by_category(findings: list[Finding]) -> dict[str, int]
```

Counts findings by category.

## Current value object

Finding analysis uses the immutable `Finding` value object instead of dict-based findings.

Suggested location:

```text
src/domain/value_objects/finding.py
```

Current shape:

```python
Finding(
    code: str,
    category: str,
    severity: str,
)
```

Suggested tests:

- multiple categories;
- one category;
- empty list;
- findings without category.

## Outside the domain

This group must not:

- render reports;
- generate API JSON;
- access a database;
- mix UI translations.

## Possible next layer

After this group is complete:

- define finding value objects/entities;
- create a report composition use case;
- expose results through the API.

---

# 10. Hash analysis

## Purpose

Pure functions for validating and normalizing already calculated hashes.

Calculating a hash by reading a file does not belong in the domain.  
Validating a hash received as a string may belong in the domain.

The implemented contract is strict on `str` inputs. The hash helpers do not accept `None`; callers must provide textual hash values.

## Suggested location

```text
src/domain/services/hash_analysis/
```

## Candidate functions

### `is_valid_sha256`

```python
is_valid_sha256(value: str) -> bool
```

Validates whether a string has SHA-256 format.

Suggested tests:

- valid lowercase hash;
- valid uppercase hash;
- invalid length;
- non-hexadecimal characters;
- empty string.

---

### `normalize_hash`

```python
normalize_hash(value: str) -> str
```

Normalizes a textual hash.

Expected behavior:

- trims spaces;
- converts to lowercase;
- does not calculate a hash.

Suggested tests:

- hash with spaces;
- uppercase;
- lowercase;
- empty string.

---

### `is_empty_hash`

```python
is_empty_hash(value: str) -> bool
```

Detects whether a hash is empty or missing.

Suggested tests:

- empty string;
- spaces;
- whitespace-only strings;
- valid hash.

## Outside the domain

This group must not:

- open files;
- read bytes;
- calculate SHA-256 from content;
- calculate hashes from attachments or filesystem paths;
- query VirusTotal or other APIs.

## Possible next layer

After this group is complete:

- `application` may request hash calculation through a port;
- `infrastructure` may implement calculation over filesystem or bytes.

---

# Recommended implementation order

Do not implement everything at once.

Suggested iteration order:

```text
1. text_normalization
2. homoglyphs
3. domain_analysis
4. url_analysis
5. attachment_analysis
6. risk_scoring
7. authentication_analysis
8. social_engineering
9. hash_analysis
10. finding_analysis
```

The first pure Domain iteration for these listed groups is complete. Future work should decide whether to move upward to Application composition, define ports for IO boundaries, or add new pure groups.

Reason:

- the first groups are simple, pure, and highly testable;
- they provide early forensic value;
- they do not require complex entities yet;
- they help establish unit testing discipline before moving up layers.

---

# Iteration template

Use this template for each group or subgroup.

```md
## Iteration N - [group/function]

Status: pending | in-progress | done

### Scope

Included functions:

- ...

Excluded functions:

- ...

### Domain contract

Proposed signature:

```python
...
```

### Unit tests

Minimum cases:

- ...
- ...

### Implementation notes

- ...
- ...

### Acceptance criteria

- [ ] The function is pure.
- [ ] There is no IO.
- [ ] There are no infrastructure imports.
- [ ] Unit tests exist.
- [ ] Tests pass.
- [ ] Behavior is documented.

### Next layer

Move to Application?

- Yes / No / Pending

Requires a port?

- Yes / No / Pending

Requires an Infrastructure adapter?

- Yes / No / Pending

### Commit

```text
...
```
```

---

# Functions explicitly outside Domain

These functions or responsibilities must not be implemented directly in `domain`:

```python
parse_eml(...)
resolve_short_url(...)
take_screenshot(...)
scan_yara(...)
run_ocr(...)
call_ollama(...)
extract_pdf_links_from_file(...)
validate_dkim_signature(...)
check_spf_dns(...)
calculate_file_hash_from_path(...)
query_virustotal(...)
download_url(...)
```

Reason:

- they require IO;
- they depend on external libraries;
- they use network access;
- they use filesystem access;
- they execute processes;
- they belong in `infrastructure`;
- they must be exposed to the domain through ports defined in `application`.

---

# Criteria for moving up layers

A function or group only moves to upper layers when:

- domain unit tests are complete;
- the contract is stable;
- the use case that needs it is understood;
- it is clear whether a port is required;
- an adapter can be created without contaminating the domain.

Example flow:

```text
contains_punycode(domain)
        ↓
domain unit tests
        ↓
AnalyzeLinksUseCase in application
        ↓
LinkAnalyzerPort if external resolution is required
        ↓
HttpRedirectResolverAdapter in infrastructure
        ↓
FastAPI endpoint if exposed to the user
```

---

# Final rule

The domain must grow slowly.

Every pure function must justify its existence through:

- real forensic value;
- unit tests;
- no external dependencies;
- a clean path to later integration through upper layers.
