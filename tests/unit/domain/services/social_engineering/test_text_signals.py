from domain.services.social_engineering.text_signals import (
    SOCIAL_ENGINEERING_CRITICAL,
    SOCIAL_ENGINEERING_HIGH,
    SOCIAL_ENGINEERING_LOW,
    SOCIAL_ENGINEERING_MEDIUM,
    classify_social_engineering_risk,
    contains_credential_request_terms,
    contains_financial_pressure_terms,
    contains_urgency_terms,
    count_social_engineering_signals,
)


def test_should_detect_urgency_phrase() -> None:
    text = "Act now to avoid account suspension."
    terms = {"act now"}

    assert contains_urgency_terms(text, terms) is True


def test_should_return_false_when_text_has_no_urgency_terms() -> None:
    text = "Your monthly report is ready."
    terms = {"urgent", "act now"}

    assert contains_urgency_terms(text, terms) is False


def test_should_detect_urgency_terms_case_insensitively() -> None:
    text = "URGENT payment review required."
    terms = {"urgent"}

    assert contains_urgency_terms(text, terms) is True


def test_should_return_false_when_text_is_empty() -> None:
    assert contains_urgency_terms("", {"urgent"}) is False


def test_should_return_false_when_terms_are_empty() -> None:
    assert contains_urgency_terms("urgent action required", set()) is False


def test_should_ignore_empty_urgency_terms() -> None:
    assert contains_urgency_terms("neutral text", {"", "   "}) is False


def test_should_detect_financial_pressure_phrase() -> None:
    text = "Your invoice is overdue and payment is required."
    terms = {"invoice is overdue"}

    assert contains_financial_pressure_terms(text, terms) is True


def test_should_return_false_when_text_has_no_financial_pressure_terms() -> None:
    text = "Your monthly report is ready."
    terms = {"payment required", "overdue invoice"}

    assert contains_financial_pressure_terms(text, terms) is False


def test_should_detect_financial_pressure_terms_case_insensitively() -> None:
    text = "PAYMENT REQUIRED before the end of the day."
    terms = {"payment required"}

    assert contains_financial_pressure_terms(text, terms) is True


def test_should_return_false_when_financial_pressure_text_is_empty() -> None:
    assert contains_financial_pressure_terms("", {"payment required"}) is False


def test_should_return_false_when_financial_pressure_terms_are_empty() -> None:
    assert contains_financial_pressure_terms("payment required", set()) is False


def test_should_ignore_empty_financial_pressure_terms() -> None:
    assert contains_financial_pressure_terms("neutral text", {"", "   "}) is False


def test_should_detect_credential_request_phrase() -> None:
    text = "Please verify your account to continue."
    terms = {"verify your account"}

    assert contains_credential_request_terms(text, terms) is True


def test_should_detect_credential_request_password_phrase() -> None:
    text = "Please confirm your password immediately."
    terms = {"confirm your password"}

    assert contains_credential_request_terms(text, terms) is True


def test_should_return_false_when_text_has_no_credential_request_terms() -> None:
    text = "Your monthly report is ready."
    terms = {"verify your account", "confirm your password"}

    assert contains_credential_request_terms(text, terms) is False


def test_should_detect_credential_request_terms_case_insensitively() -> None:
    text = "CONFIRM YOUR LOGIN before continuing."
    terms = {"confirm your login"}

    assert contains_credential_request_terms(text, terms) is True


def test_should_return_false_when_credential_request_text_is_empty() -> None:
    assert contains_credential_request_terms("", {"confirm your password"}) is False


def test_should_return_false_when_credential_request_terms_are_empty() -> None:
    assert contains_credential_request_terms("password reset required", set()) is False


def test_should_ignore_empty_credential_request_terms() -> None:
    assert contains_credential_request_terms("neutral text", {"", "   "}) is False


def test_should_count_social_engineering_signals_by_category() -> None:
    text = "Urgent payment required. Verify your account."
    signal_terms = {
        "urgency": {"urgent"},
        "financial_pressure": {"payment required"},
        "credential_request": {"verify your account"},
    }

    assert count_social_engineering_signals(text, signal_terms) == {
        "urgency": 1,
        "financial_pressure": 1,
        "credential_request": 1,
    }


def test_should_count_multiple_terms_in_same_social_engineering_category() -> None:
    text = "Urgent action required. Act now to keep access."
    signal_terms = {
        "urgency": {"urgent", "act now"},
    }

    assert count_social_engineering_signals(text, signal_terms) == {"urgency": 2}


def test_should_preserve_social_engineering_categories_with_zero_count() -> None:
    text = "Your monthly report is ready."
    signal_terms = {
        "urgency": {"urgent"},
        "credential_request": {"confirm your password"},
    }

    assert count_social_engineering_signals(text, signal_terms) == {
        "urgency": 0,
        "credential_request": 0,
    }


def test_should_not_treat_generic_password_reset_wording_as_credential_request() -> None:
    text = "We received a request to reset your password."
    terms = {"confirm your password", "enter your password", "verify your account"}

    assert contains_credential_request_terms(text, terms) is False


def test_should_return_zero_counts_when_social_engineering_text_is_empty() -> None:
    signal_terms = {
        "urgency": {"urgent"},
        "financial_pressure": {"payment required"},
    }

    assert count_social_engineering_signals("", signal_terms) == {
        "urgency": 0,
        "financial_pressure": 0,
    }


def test_should_return_empty_counts_when_social_engineering_terms_are_empty() -> None:
    assert count_social_engineering_signals("urgent payment required", {}) == {}


def test_should_ignore_empty_social_engineering_terms_when_counting() -> None:
    text = "Urgent action required."
    signal_terms = {
        "urgency": {"", "   ", "urgent"},
    }

    assert count_social_engineering_signals(text, signal_terms) == {"urgency": 1}


def test_should_count_social_engineering_signals_case_insensitively() -> None:
    text = "URGENT payment REQUIRED."
    signal_terms = {
        "urgency": {"urgent"},
        "financial_pressure": {"payment required"},
    }

    assert count_social_engineering_signals(text, signal_terms) == {
        "urgency": 1,
        "financial_pressure": 1,
    }


def test_should_classify_social_engineering_risk_as_low_without_signals() -> None:
    assert classify_social_engineering_risk({}) == SOCIAL_ENGINEERING_LOW
    assert classify_social_engineering_risk({"urgency": 0}) == SOCIAL_ENGINEERING_LOW


def test_should_classify_social_engineering_risk_as_medium_with_one_signal() -> None:
    assert classify_social_engineering_risk({"urgency": 1}) == SOCIAL_ENGINEERING_MEDIUM


def test_should_classify_social_engineering_risk_as_high_with_two_signals() -> None:
    assert classify_social_engineering_risk(
        {
            "urgency": 1,
            "financial_pressure": 1,
        }
    ) == SOCIAL_ENGINEERING_HIGH


def test_should_classify_social_engineering_risk_as_critical_with_three_or_more_signals() -> None:
    assert classify_social_engineering_risk(
        {
            "urgency": 1,
            "financial_pressure": 1,
            "credential_request": 1,
        }
    ) == SOCIAL_ENGINEERING_CRITICAL
    assert classify_social_engineering_risk({"urgency": 4}) == SOCIAL_ENGINEERING_CRITICAL


def test_should_ignore_negative_counts_when_classifying_social_engineering_risk() -> None:
    assert classify_social_engineering_risk(
        {
            "urgency": 1,
            "mitigating_signal": -5,
        }
    ) == SOCIAL_ENGINEERING_MEDIUM
