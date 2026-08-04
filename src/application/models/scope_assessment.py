from dataclasses import dataclass
import re

from application.models.extracted_email import ExtractedEmailContent


SCOPE_FAMILY_ACCOUNT = "account"
SCOPE_FAMILY_MFA_SECURITY = "mfa_security"
SCOPE_FAMILY_CLOUD_DOCUMENT_SHARING = "cloud_document_sharing"
SCOPE_FAMILY_BILLING_INVOICES = "billing_invoices"
SCOPE_FAMILY_SUPPORT = "support"
SCOPE_FAMILY_HR = "hr"
SCOPE_FAMILY_VENDOR_PORTALS = "vendor_portals"
SCOPE_FAMILY_NEWSLETTER_PREFERENCES = "newsletter_preferences"
SCOPE_FAMILY_OUT_OF_SCOPE = "out_of_scope"

SCOPE_REASON_IN_SCOPE = "in_scope_family"
SCOPE_REASON_EMPTY_CONTENT = "empty_content"
SCOPE_REASON_URL_ONLY = "url_only"
SCOPE_REASON_NO_FAMILY_SIGNAL = "no_family_signal"


@dataclass(frozen=True)
class ScopeAssessment:
    family: str
    confidence: float
    reason: str


_FAMILY_TERMS: dict[str, tuple[str, ...]] = {
    SCOPE_FAMILY_ACCOUNT: ("account", "profile", "sign in", "login", "password"),
    SCOPE_FAMILY_MFA_SECURITY: ("mfa", "multi-factor", "multifactor", "security", "verification code", "two-factor"),
    SCOPE_FAMILY_CLOUD_DOCUMENT_SHARING: ("cloud", "storage", "document", "shared", "share", "workspace"),
    SCOPE_FAMILY_BILLING_INVOICES: ("invoice", "billing", "bill", "payment", "receipt", "renewal"),
    SCOPE_FAMILY_SUPPORT: ("support", "ticket", "case", "helpdesk", "customer service"),
    SCOPE_FAMILY_HR: ("hr", "human resources", "benefits", "payroll", "employee", "employment"),
    SCOPE_FAMILY_VENDOR_PORTALS: ("vendor", "supplier", "procurement", "vendor portal", "purchase order"),
    SCOPE_FAMILY_NEWSLETTER_PREFERENCES: ("newsletter", "unsubscribe", "preferences", "digest", "subscription"),
}

_STRONG_FAMILY_TERMS: dict[str, tuple[str, ...]] = {
    SCOPE_FAMILY_ACCOUNT: ("account activity", "account summary", "account usage", "login", "sign in", "password", "verify your account", "account profile"),
    SCOPE_FAMILY_MFA_SECURITY: ("mfa", "multi-factor", "multifactor", "verification code", "two-factor", "recovery codes", "security alert", "new sign-in", "security alert login"),
    SCOPE_FAMILY_BILLING_INVOICES: ("invoice", "billing", "payment", "receipt", "renewal"),
    SCOPE_FAMILY_CLOUD_DOCUMENT_SHARING: ("cloud", "storage", "shared", "share", "workspace"),
    SCOPE_FAMILY_SUPPORT: ("support", "ticket", "case", "helpdesk", "customer service"),
    SCOPE_FAMILY_HR: ("human resources", "benefits", "payroll", "employee", "employment"),
    SCOPE_FAMILY_VENDOR_PORTALS: ("vendor", "supplier", "procurement", "vendor portal", "purchase order", "invoice portal"),
    SCOPE_FAMILY_NEWSLETTER_PREFERENCES: ("newsletter", "unsubscribe", "preferences", "digest", "subscription", "newsletter includes", "newsletter security"),
}


def assess_email_scope(email: ExtractedEmailContent) -> ScopeAssessment:
    content = " ".join((email.subject, email.body_text)).strip().lower()
    if not content:
        return ScopeAssessment(SCOPE_FAMILY_OUT_OF_SCOPE, 1.0, SCOPE_REASON_EMPTY_CONTENT)

    if not email.subject.strip() and not email.body_text.strip():
        return ScopeAssessment(SCOPE_FAMILY_OUT_OF_SCOPE, 1.0, SCOPE_REASON_EMPTY_CONTENT)

    if _is_url_only_content(content, email.urls):
        return ScopeAssessment(SCOPE_FAMILY_OUT_OF_SCOPE, 1.0, SCOPE_REASON_URL_ONLY)

    strong_scores = {
        family: sum(term in content for term in terms)
        for family, terms in _STRONG_FAMILY_TERMS.items()
    }
    strongest_family, strongest_score = max(strong_scores.items(), key=lambda item: item[1])
    if strongest_score > 0:
        family = strongest_family
        score = strongest_score
        second_score = sorted(strong_scores.values(), reverse=True)[1]
    else:
        return ScopeAssessment(SCOPE_FAMILY_OUT_OF_SCOPE, 0.0, SCOPE_REASON_NO_FAMILY_SIGNAL)
    if score < 1:
        return ScopeAssessment(SCOPE_FAMILY_OUT_OF_SCOPE, 0.0, SCOPE_REASON_NO_FAMILY_SIGNAL)

    confidence = min(1.0, 0.5 + 0.15 * score + 0.1 * max(0, score - second_score))
    return ScopeAssessment(family, confidence, SCOPE_REASON_IN_SCOPE)


def _is_url_only_content(content: str, urls: tuple[str, ...]) -> bool:
    if urls and not content.replace(" ", ""):
        return True
    return bool(re.fullmatch(r"(?:https?://\S+\s*)+", content))
