import hashlib
import re
from dataclasses import dataclass

from tools.ml_data_preparation.prepared_email_sample import PreparedEmailSample


SYNTHETIC_BENIGN_NOTIFICATIONS_SOURCE = "synthetic_benign_notifications"
SYNTHETIC_BENIGN_NOTIFICATIONS_SOURCE_URI = "synthetic://phishshield/benign-notifications"
SYNTHETIC_BENIGN_ORIGINAL_LABEL = "synthetic_benign"
NORMALIZED_LABEL_BENIGN = "benign"

_HTTP_URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
_TRAILING_URL_PUNCTUATION = ".,;:!?) ]"


@dataclass(frozen=True)
class SyntheticBenignNotificationTemplate:
    category: str
    template_id: str
    sender_domain: str
    subject: str
    body_text: str


_CATEGORIES: tuple[str, ...] = (
    "account_activity_summary",
    "account_usage_digest",
    "mfa_enabled_notice",
    "security_login_notice",
    "password_reset_confirmation",
    "newsletter_product_update",
    "account_preferences_update",
    "cloud_document_share_notice",
    "billing_receipt",
    "support_ticket_update",
    "hr_policy_update",
    "vendor_portal_notice",
)


def iter_synthetic_benign_notification_templates(
    samples_per_category: int = 10,
) -> tuple[SyntheticBenignNotificationTemplate, ...]:
    if samples_per_category < 0:
        raise ValueError("samples_per_category must be greater than or equal to zero")

    templates: list[SyntheticBenignNotificationTemplate] = []
    for category in _CATEGORIES:
        for index in range(1, samples_per_category + 1):
            templates.append(_build_template(category=category, index=index))

    return tuple(templates)


def prepare_synthetic_benign_notification_template(
    template: SyntheticBenignNotificationTemplate,
) -> PreparedEmailSample:
    urls = _extract_urls_from_text(template.body_text)
    source_id = f"{template.category}-{template.template_id}"
    sample_id = _build_sample_id(
        source=SYNTHETIC_BENIGN_NOTIFICATIONS_SOURCE,
        source_id=source_id,
        subject=template.subject,
        body_text=template.body_text,
        urls=urls,
    )

    return PreparedEmailSample(
        sample_id=sample_id,
        source=SYNTHETIC_BENIGN_NOTIFICATIONS_SOURCE,
        source_id=source_id,
        source_uri=SYNTHETIC_BENIGN_NOTIFICATIONS_SOURCE_URI,
        original_label=SYNTHETIC_BENIGN_ORIGINAL_LABEL,
        normalized_label=NORMALIZED_LABEL_BENIGN,
        subject=template.subject,
        body_text=template.body_text,
        sender_domain=template.sender_domain,
        urls=urls,
        attachment_filenames=(),
        raw_available=False,
        metadata={
            "category": template.category,
            "template_id": template.template_id,
            "original_label": SYNTHETIC_BENIGN_ORIGINAL_LABEL,
        },
    )


def _build_template(category: str, index: int) -> SyntheticBenignNotificationTemplate:
    variants = _CATEGORY_VARIANTS[category]
    variant = variants[(index - 1) % len(variants)]
    template_id = f"{index:03d}"
    url_slug = f"{category.replace('_', '-')}-{index:03d}"
    sender_domain = variant["sender_domain"]
    subject = variant["subject"].format(index=index)
    body_text = variant["body_text"].format(
        index=index,
        sender_domain=sender_domain,
        url_slug=url_slug,
    )

    return SyntheticBenignNotificationTemplate(
        category=category,
        template_id=template_id,
        sender_domain=sender_domain,
        subject=subject,
        body_text=body_text,
    )


def _extract_urls_from_text(text: str) -> tuple[str, ...]:
    return tuple(
        match.group(0).rstrip(_TRAILING_URL_PUNCTUATION)
        for match in _HTTP_URL_PATTERN.finditer(text)
    )


def _build_sample_id(
    source: str,
    source_id: str,
    subject: str,
    body_text: str,
    urls: tuple[str, ...],
) -> str:
    hash_input = "\n".join((source, source_id, NORMALIZED_LABEL_BENIGN, subject, body_text, "\n".join(urls)))

    return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()


_CATEGORY_VARIANTS: dict[str, tuple[dict[str, str], ...]] = {
    "account_activity_summary": (
        {
            "sender_domain": "accounts.example.com",
            "subject": "Account activity summary #{index}",
            "body_text": "Your account activity summary is ready. Review trusted sign-ins and usage history at https://{sender_domain}/activity/{url_slug}. No action is required.",
        },
        {
            "sender_domain": "profile.example.com",
            "subject": "Recent account activity digest #{index}",
            "body_text": "We prepared your recent account activity digest for your records. Open your normal dashboard at https://{sender_domain}/dashboard/{url_slug} when convenient.",
        },
    ),
    "account_usage_digest": (
        {
            "sender_domain": "usage.example.com",
            "subject": "Monthly usage digest #{index}",
            "body_text": "Your monthly usage digest shows storage, login, and notification settings for your workspace. Details are available at https://{sender_domain}/usage/{url_slug}.",
        },
        {
            "sender_domain": "workspace.example.com",
            "subject": "Workspace account usage report #{index}",
            "body_text": "This account usage report is informational and does not require confirmation. View the report at https://{sender_domain}/reports/{url_slug}.",
        },
    ),
    "mfa_enabled_notice": (
        {
            "sender_domain": "identity.example.com",
            "subject": "Multi-factor authentication enabled #{index}",
            "body_text": "Multi-factor authentication was enabled for your account from security settings. If this was you, no action is needed. Review activity at https://{sender_domain}/security/{url_slug}.",
        },
        {
            "sender_domain": "auth.example.com",
            "subject": "MFA settings changed #{index}",
            "body_text": "Your MFA settings changed successfully. This notification confirms the change and does not ask for your password. See https://{sender_domain}/settings/{url_slug}.",
        },
    ),
    "security_login_notice": (
        {
            "sender_domain": "security.example.com",
            "subject": "New sign-in notification #{index}",
            "body_text": "We noticed a successful sign-in from a trusted browser. If this was you, no further action is required. Activity details: https://{sender_domain}/login-activity/{url_slug}.",
        },
        {
            "sender_domain": "accounts.example.com",
            "subject": "Security activity notice #{index}",
            "body_text": "A normal security activity notice was added to your account history. You can review it later at https://{sender_domain}/security/activity/{url_slug}.",
        },
    ),
    "password_reset_confirmation": (
        {
            "sender_domain": "accounts.example.com",
            "subject": "Password reset completed #{index}",
            "body_text": "Your password reset was completed successfully. This message is a confirmation only and does not require entering your password. Visit https://{sender_domain}/help/{url_slug} for support.",
        },
        {
            "sender_domain": "support.example.com",
            "subject": "Password change confirmation #{index}",
            "body_text": "This confirms your password was changed. If you did not request this, contact support from https://{sender_domain}/contact/{url_slug}.",
        },
    ),
    "newsletter_product_update": (
        {
            "sender_domain": "updates.example.com",
            "subject": "Product update newsletter #{index}",
            "body_text": "This week's newsletter includes product updates, account preference tips, and release notes. Read more at https://{sender_domain}/newsletter/{url_slug}.",
        },
        {
            "sender_domain": "news.example.com",
            "subject": "Feature highlights digest #{index}",
            "body_text": "Your feature highlights digest is ready. It includes dashboard improvements and notification preferences at https://{sender_domain}/digest/{url_slug}.",
        },
    ),
    "account_preferences_update": (
        {
            "sender_domain": "preferences.example.com",
            "subject": "Account preferences updated #{index}",
            "body_text": "Your account preferences were updated from the settings page. Review notification and privacy settings at https://{sender_domain}/preferences/{url_slug}.",
        },
        {
            "sender_domain": "profile.example.com",
            "subject": "Notification preferences changed #{index}",
            "body_text": "This confirms notification preferences changed for your account. No verification is required. Details: https://{sender_domain}/notifications/{url_slug}.",
        },
    ),
    "cloud_document_share_notice": (
        {
            "sender_domain": "docs.example.com",
            "subject": "Document shared with you #{index}",
            "body_text": "A teammate shared a planning document with you. Open it from your workspace document list at https://{sender_domain}/documents/{url_slug}.",
        },
        {
            "sender_domain": "drive.example.com",
            "subject": "Shared folder notification #{index}",
            "body_text": "You received access to a shared folder. This notification is informational. View folder details at https://{sender_domain}/shared/{url_slug}.",
        },
    ),
    "billing_receipt": (
        {
            "sender_domain": "billing.example.com",
            "subject": "Payment receipt #{index}",
            "body_text": "Your payment receipt is available for download from the billing portal. View receipt details at https://{sender_domain}/receipts/{url_slug}.",
        },
        {
            "sender_domain": "payments.example.com",
            "subject": "Invoice paid confirmation #{index}",
            "body_text": "Invoice payment was received successfully. This is a receipt confirmation only. Details: https://{sender_domain}/invoice/{url_slug}.",
        },
    ),
    "support_ticket_update": (
        {
            "sender_domain": "support.example.com",
            "subject": "Support ticket updated #{index}",
            "body_text": "Your support ticket has a new comment from our team. Review the update at https://{sender_domain}/tickets/{url_slug}.",
        },
        {
            "sender_domain": "helpdesk.example.com",
            "subject": "Help desk case status #{index}",
            "body_text": "Your help desk case status changed to waiting for customer review. See the case at https://{sender_domain}/case/{url_slug}.",
        },
    ),
    "hr_policy_update": (
        {
            "sender_domain": "hr.example.com",
            "subject": "HR policy update #{index}",
            "body_text": "A new HR policy update is available in the employee portal. Read the policy at https://{sender_domain}/policies/{url_slug}.",
        },
        {
            "sender_domain": "people.example.com",
            "subject": "Benefits enrollment reminder #{index}",
            "body_text": "Benefits enrollment opens soon. Review plan dates and options at https://{sender_domain}/benefits/{url_slug}.",
        },
    ),
    "vendor_portal_notice": (
        {
            "sender_domain": "vendor.example.com",
            "subject": "Vendor portal notice #{index}",
            "body_text": "A vendor portal notice was posted for your organization. Review purchase order updates at https://{sender_domain}/portal/{url_slug}.",
        },
        {
            "sender_domain": "procurement.example.com",
            "subject": "Supplier account update #{index}",
            "body_text": "Supplier account information was updated by the procurement team. Details are available at https://{sender_domain}/suppliers/{url_slug}.",
        },
    ),
}
