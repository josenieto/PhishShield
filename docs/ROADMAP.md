# PhishShield Roadmap

This roadmap communicates project direction. Community suggestions are welcome
through GitHub Discussions, but maintainers retain final ownership of
prioritization, scope, and delivery. Roadmap items are not delivery commitments.

## Available Now

- deterministic `.eml` phishing-email triage;
- analyst Web UI;
- FastAPI API;
- single-email deterministic CLI;
- sender, URL, attachment, authentication, and social-engineering evidence;
- explainable findings and deterministic risk score;
- Markdown, JSON, and HTML exports;
- GitHub Actions artifact analysis workflow;
- local-first runtime and experimental advisory model boundary.

## Planned Directions

These are project-owned directions that may be prioritized after RC.2:

- complete and validate the one-command Docker Compose product deployment;
- batch CLI analysis when a real folder-analysis workflow justifies it;
- JSONL output for concrete automation workflows;
- SARIF integration for a demonstrated security-platform use case;
- parser improvements driven by reproducible email samples;
- reporting and analyst workflow improvements driven by usage;
- optional local history only if privacy and maintenance costs are justified;
- family-specific advisory training only with authorized, independently evaluated data.

## Explicitly Deferred

- OCR;
- YARA scanning;
- PDF and Office parsing beyond current metadata scope;
- macro analysis;
- browser or sandbox evidence capture;
- short-link resolution;
- attachment reputation lookups;
- production-grade advisory model promotion;
- cloud hosting as a required dependency;
- accounts, persistence, and multi-user operation.

## Feedback Boundary

Use GitHub Discussions for ideas, use cases, and deployment feedback. Do not
submit real corporate email or sensitive samples through public GitHub channels.
A suggestion does not create a commitment to implement the requested feature.
