import hashlib
import re
from dataclasses import dataclass

from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample


SYNTHETIC_SUSPICIOUS_NOTIFICATIONS_SOURCE = "synthetic_suspicious_notifications"
SYNTHETIC_SUSPICIOUS_NOTIFICATIONS_SOURCE_URI = "synthetic://phishshield/suspicious-notifications"
SYNTHETIC_SUSPICIOUS_ORIGINAL_LABEL = "synthetic_suspicious"
NORMALIZED_LABEL_SUSPICIOUS = "suspicious"

_HTTP_URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
_TRAILING_URL_PUNCTUATION = ".,;:!?) ]"


@dataclass(frozen=True)
class SyntheticSuspiciousNotificationTemplate:
    category: str
    template_id: str
    sender_domain: str
    subject: str
    body_text: str


_CATEGORIES: tuple[str, ...] = (
    "account_activity_verification_lure",
    "account_usage_suspension_lure",
    "mfa_push_approval_lure",
    "security_login_verification_lure",
    "password_reset_portal_lure",
    "newsletter_account_preferences_lure",
    "cloud_document_review_lure",
    "billing_payment_confirmation_lure",
    "support_ticket_credential_lure",
    "hr_policy_acknowledgement_lure",
    "vendor_portal_reauthentication_lure",
    "storage_quota_verification_lure",
)


def iter_synthetic_suspicious_notification_templates(
    samples_per_category: int = 10,
) -> tuple[SyntheticSuspiciousNotificationTemplate, ...]:
    if samples_per_category < 0:
        raise ValueError("samples_per_category must be greater than or equal to zero")

    templates: list[SyntheticSuspiciousNotificationTemplate] = []
    for category in _CATEGORIES:
        for index in range(1, samples_per_category + 1):
            templates.append(_build_template(category=category, index=index))

    return tuple(templates)


def prepare_synthetic_suspicious_notification_template(
    template: SyntheticSuspiciousNotificationTemplate,
) -> PreparedEmailSample:
    urls = _extract_urls_from_text(template.body_text)
    source_id = f"{template.category}-{template.template_id}"
    sample_id = _build_sample_id(
        source=SYNTHETIC_SUSPICIOUS_NOTIFICATIONS_SOURCE,
        source_id=source_id,
        subject=template.subject,
        body_text=template.body_text,
        urls=urls,
    )

    return PreparedEmailSample(
        sample_id=sample_id,
        source=SYNTHETIC_SUSPICIOUS_NOTIFICATIONS_SOURCE,
        source_id=source_id,
        source_uri=SYNTHETIC_SUSPICIOUS_NOTIFICATIONS_SOURCE_URI,
        original_label=SYNTHETIC_SUSPICIOUS_ORIGINAL_LABEL,
        normalized_label=NORMALIZED_LABEL_SUSPICIOUS,
        subject=template.subject,
        body_text=template.body_text,
        sender_domain=template.sender_domain,
        urls=urls,
        attachment_filenames=(),
        raw_available=False,
        metadata={
            "category": template.category,
            "template_id": template.template_id,
            "original_label": SYNTHETIC_SUSPICIOUS_ORIGINAL_LABEL,
        },
    )


def _build_template(category: str, index: int) -> SyntheticSuspiciousNotificationTemplate:
    variants = _CATEGORY_VARIANTS[category]
    variant = variants[(index - 1) % len(variants)]
    template_id = f"{index:03d}"
    url_slug = f"{category.replace('_', '-')}-{index:03d}"
    sender_domain = variant["sender_domain"]
    subject = variant["subject"].format(index=index)
    body_text = variant["body_text"].format(sender_domain=sender_domain, url_slug=url_slug)

    return SyntheticSuspiciousNotificationTemplate(
        category=category,
        template_id=template_id,
        sender_domain=sender_domain,
        subject=subject,
        body_text=body_text,
    )


def _extract_urls_from_text(text: str) -> tuple[str, ...]:
    return tuple(match.group(0).rstrip(_TRAILING_URL_PUNCTUATION) for match in _HTTP_URL_PATTERN.finditer(text))


def _build_sample_id(source: str, source_id: str, subject: str, body_text: str, urls: tuple[str, ...]) -> str:
    hash_input = "\n".join((source, source_id, NORMALIZED_LABEL_SUSPICIOUS, subject, body_text, "\n".join(urls)))
    return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()


_CATEGORY_VARIANTS: dict[str, tuple[dict[str, str], ...]] = {
    "account_activity_verification_lure": (
        {"sender_domain": "secure-account-review.example.net", "subject": "Account activity verification required #{index}", "body_text": "Unusual account activity requires verification. Confirm your login at https://{sender_domain}/verify/{url_slug} to keep access active."},
        {"sender_domain": "account-activity-check.example.net", "subject": "Review account activity now #{index}", "body_text": "Your account activity review is pending. Verify your account at https://{sender_domain}/account/{url_slug} before access is limited."},
    ),
    "account_usage_suspension_lure": (
        {"sender_domain": "usage-suspension.example.net", "subject": "Account usage suspension warning #{index}", "body_text": "Your account usage triggered a suspension review. Confirm your login at https://{sender_domain}/restore/{url_slug} to avoid interruption."},
        {"sender_domain": "workspace-access.example.net", "subject": "Workspace usage must be confirmed #{index}", "body_text": "Workspace access will be paused unless you verify account usage at https://{sender_domain}/confirm/{url_slug}."},
    ),
    "mfa_push_approval_lure": (
        {"sender_domain": "mfa-approval-center.example.net", "subject": "MFA approval required #{index}", "body_text": "Approve the pending MFA request to keep your account active: https://{sender_domain}/mfa/{url_slug}."},
        {"sender_domain": "secure-mfa-review.example.net", "subject": "Multi-factor authentication review #{index}", "body_text": "Your MFA settings require immediate review. Confirm your login at https://{sender_domain}/review/{url_slug}."},
    ),
    "security_login_verification_lure": (
        {"sender_domain": "security-login-review.example.net", "subject": "New sign-in verification #{index}", "body_text": "A new sign-in must be verified. Confirm your login at https://{sender_domain}/signin/{url_slug} within 24 hours."},
        {"sender_domain": "identity-security-check.example.net", "subject": "Security login action required #{index}", "body_text": "Security policy requires account verification. Continue at https://{sender_domain}/security/{url_slug}."},
    ),
    "password_reset_portal_lure": (
        {"sender_domain": "password-portal.example.net", "subject": "Password reset portal notice #{index}", "body_text": "Your password reset request is pending. Enter your password at https://{sender_domain}/reset/{url_slug} to confirm."},
        {"sender_domain": "credential-reset.example.net", "subject": "Confirm password reset #{index}", "body_text": "Confirm your password reset immediately at https://{sender_domain}/confirm/{url_slug} to keep access."},
    ),
    "newsletter_account_preferences_lure": (
        {"sender_domain": "newsletter-preferences.example.net", "subject": "Account preferences verification #{index}", "body_text": "Your newsletter account preferences require verification. Confirm your login at https://{sender_domain}/preferences/{url_slug}."},
        {"sender_domain": "updates-account.example.net", "subject": "Product update settings locked #{index}", "body_text": "Product update settings are locked until you verify your account at https://{sender_domain}/settings/{url_slug}."},
    ),
    "cloud_document_review_lure": (
        {"sender_domain": "cloud-docs-review.example.net", "subject": "Shared document requires review #{index}", "body_text": "A protected cloud document requires account verification. Open it at https://{sender_domain}/document/{url_slug}."},
        {"sender_domain": "secure-share-review.example.net", "subject": "Cloud share access pending #{index}", "body_text": "Your shared folder access will expire unless you confirm your login at https://{sender_domain}/share/{url_slug}."},
    ),
    "billing_payment_confirmation_lure": (
        {"sender_domain": "billing-profile-confirm.example.net", "subject": "Payment profile confirmation #{index}", "body_text": "Your billing profile must be confirmed before invoice release. Continue at https://{sender_domain}/billing/{url_slug}."},
        {"sender_domain": "invoice-payment-review.example.net", "subject": "Invoice payment verification #{index}", "body_text": "Confirm your payment details for the pending invoice at https://{sender_domain}/invoice/{url_slug}."},
    ),
    "support_ticket_credential_lure": (
        {"sender_domain": "support-ticket-auth.example.net", "subject": "Support ticket requires login #{index}", "body_text": "Your support ticket requires credential verification. Confirm your login at https://{sender_domain}/ticket/{url_slug}."},
        {"sender_domain": "helpdesk-auth-review.example.net", "subject": "Help desk case authentication #{index}", "body_text": "Authenticate to keep your help desk case open at https://{sender_domain}/case/{url_slug}."},
    ),
    "hr_policy_acknowledgement_lure": (
        {"sender_domain": "hr-policy-review.example.net", "subject": "HR policy acknowledgement required #{index}", "body_text": "A policy acknowledgement is required. Confirm your account at https://{sender_domain}/policy/{url_slug}."},
        {"sender_domain": "employee-access-review.example.net", "subject": "Employee portal access review #{index}", "body_text": "Your employee portal access requires verification at https://{sender_domain}/employee/{url_slug}."},
    ),
    "vendor_portal_reauthentication_lure": (
        {"sender_domain": "vendor-portal-auth.example.net", "subject": "Vendor portal reauthentication #{index}", "body_text": "Reauthenticate your vendor portal account at https://{sender_domain}/portal/{url_slug} to keep purchase order access."},
        {"sender_domain": "procurement-login-review.example.net", "subject": "Supplier login confirmation #{index}", "body_text": "Supplier login confirmation is required at https://{sender_domain}/supplier/{url_slug}."},
    ),
    "storage_quota_verification_lure": (
        {"sender_domain": "storage-quota-review.example.net", "subject": "Cloud storage quota locked #{index}", "body_text": "Your cloud storage quota is locked until you confirm your login at https://{sender_domain}/quota/{url_slug}."},
        {"sender_domain": "cloud-storage-restore.example.net", "subject": "Restore shared storage access #{index}", "body_text": "Restore shared storage access by verifying your account at https://{sender_domain}/restore/{url_slug}."},
    ),
}
