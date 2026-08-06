# Security Policy

## Reporting A Vulnerability

Use GitHub's **Private Vulnerability Reporting** feature for this repository.
Do not open a public issue with vulnerability details.

If private reporting is unavailable, open a public issue only to request a
private contact channel. Do not include technical details, proof of concept,
credentials, or sensitive data in that issue.

## Do Not Publish Sensitive Material

Do not post the following in public issues, discussions, pull requests, or
attachments:

- credentials, tokens, or private keys;
- confidential or personal email;
- active malicious attachments;
- sensitive URLs or internal infrastructure details;
- customer, employee, or organizational data.

Use sanitized synthetic examples or minimal fixtures when reporting a parser or
analysis issue.

## Product Security Scope

PhishShield is a local-first email-triage tool. The deterministic analysis is
evidence and not a malware verdict. It does not execute attachments, resolve
links, render webpages, or replace organizational email-security controls.

The optional advisory model is experimental, disabled by default, and must not
be treated as a production security gate.

## Deployment Guidance

Do not expose a local or public deployment without reviewing:

- upload limits;
- network exposure;
- reverse-proxy access controls;
- log retention;
- privacy warnings;
- handling of uploaded email content.
