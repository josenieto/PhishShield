# Distribution Messages

These drafts are intended for feedback-oriented posts. Adapt them to each
community's rules and avoid posting the same text simultaneously everywhere.

## LinkedIn

I have published the first public release candidate of PhishShield.

It is a local tool for inspecting suspicious `.eml` files without opening them
in a normal mail client. It extracts sender, authentication, URL, attachment,
and social-engineering evidence, then produces deterministic findings and an
exportable report.

I am not trying to replace a mail gateway or sandbox. I am validating whether
this is useful at the point where help desk or SOC teams receive a reported
email and need a safe, explainable first look.

I would value feedback from people who handle this workflow:
<https://github.com/josenieto/PhishShield>

## Reddit Or Technical Community

I am building PhishShield, a local tool for inspecting suspicious `.eml` files
without opening them in a mail client. It extracts sender identity,
authentication results, URLs, attachment metadata, and phishing indicators. It
does not execute attachments or resolve links.

The repository includes a synthetic sample and a Docker-based two-minute demo.
I am looking for technical criticism of the workflow rather than generic
promotion: what evidence or output would you expect before integrating a tool
like this into SOC, DFIR, help-desk, or self-hosted workflows?

<https://github.com/josenieto/PhishShield>
