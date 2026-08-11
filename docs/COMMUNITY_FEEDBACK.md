# Community Feedback

Use this discussion prompt to validate the workflow with security analysts,
help-desk teams, DFIR practitioners, and self-hosting users:

## Discussion Title

In which part of your email-triage workflow would local `.eml` analysis help?

## Discussion Body

I am validating PhishShield, a local and explainable tool for inspecting
suspicious `.eml` files without opening them in a normal mail client.

It extracts sender identity, authentication results, URLs, attachment metadata,
and social-engineering indicators. It presents deterministic findings and can
export evidence as Markdown, JSON, or HTML.

PhishShield is not intended to replace a mail gateway, sandbox, malware verdict,
or incident-response process. I want to understand whether this fits a real
workflow before expanding the roadmap.

The two-minute demo uses a synthetic message:

<https://github.com/josenieto/PhishShield/tree/integration/master/samples>

The questions I would value feedback on are:

1. Who receives and analyzes `.eml` files in your team?
2. What evidence do you need before escalating a reported email?
3. Which report format or integration would be most useful?
4. What would stop you from trying a local Docker-based tool?

Please do not post real corporate email, credentials, active malicious files, or
confidential data in the discussion.
