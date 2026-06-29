from domain.services.hash_analysis.hashes import (
    is_empty_hash,
    is_valid_sha256,
    normalize_hash,
)


VALID_SHA256_LOWERCASE = (
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
)

VALID_SHA256_UPPERCASE = (
    "0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF"
)


def test_should_trim_hash_whitespace() -> None:
    assert normalize_hash("  abc123  ") == "abc123"


def test_should_lowercase_hash() -> None:
    assert normalize_hash("ABCDEF123") == "abcdef123"


def test_should_keep_lowercase_hash_unchanged() -> None:
    assert normalize_hash("abcdef123") == "abcdef123"


def test_should_return_empty_string_when_hash_is_empty() -> None:
    assert normalize_hash("") == ""


def test_should_return_empty_string_when_hash_is_whitespace_only() -> None:
    assert normalize_hash("   ") == ""


def test_should_detect_empty_hash() -> None:
    assert is_empty_hash("") is True


def test_should_detect_whitespace_only_hash_as_empty() -> None:
    assert is_empty_hash("   ") is True


def test_should_return_false_when_hash_is_not_empty() -> None:
    assert is_empty_hash("abcdef123") is False


def test_should_detect_valid_lowercase_sha256() -> None:
    assert is_valid_sha256(VALID_SHA256_LOWERCASE) is True


def test_should_detect_valid_uppercase_sha256() -> None:
    assert is_valid_sha256(VALID_SHA256_UPPERCASE) is True


def test_should_detect_valid_sha256_with_surrounding_spaces() -> None:
    assert is_valid_sha256(f"  {VALID_SHA256_LOWERCASE}  ") is True


def test_should_return_false_when_sha256_length_is_invalid() -> None:
    assert is_valid_sha256("abc123") is False


def test_should_return_false_when_sha256_contains_non_hexadecimal_characters() -> None:
    invalid_hash = "g" * 64

    assert is_valid_sha256(invalid_hash) is False


def test_should_return_false_when_sha256_is_empty() -> None:
    assert is_valid_sha256("") is False


def test_should_return_false_when_sha256_is_whitespace_only() -> None:
    assert is_valid_sha256("   ") is False
