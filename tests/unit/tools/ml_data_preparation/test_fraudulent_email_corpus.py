from tools.ml_data_preparation.fraudulent_email_corpus import (
    FRAUDULENT_EMAIL_CORPUS_ORIGINAL_LABEL,
    FRAUDULENT_EMAIL_CORPUS_SOURCE,
    FRAUDULENT_EMAIL_CORPUS_SOURCE_URI,
    NORMALIZED_LABEL_SUSPICIOUS,
    prepare_fraudulent_email_corpus_message,
    split_fraudulent_email_corpus_message_bytes,
    split_fraudulent_email_corpus_messages,
)


def test_should_split_corpus_text_into_messages() -> None:
    messages = split_fraudulent_email_corpus_messages(_sample_corpus_text())

    assert len(messages) == 2
    assert messages[0].startswith("Return-Path:")
    assert "Subject: First proposal" in messages[0]
    assert messages[1].startswith("Return-Path:")
    assert "Subject: Second proposal" in messages[1]


def test_should_return_empty_tuple_when_no_message_boundary_exists() -> None:
    assert split_fraudulent_email_corpus_messages("plain text without email headers") == ()


def test_should_split_corpus_bytes_into_messages() -> None:
    messages = split_fraudulent_email_corpus_message_bytes(_sample_corpus_text().encode("utf-8"))

    assert len(messages) == 2
    assert messages[0].startswith(b"Return-Path:")
    assert b"Subject: First proposal" in messages[0]
    assert messages[1].startswith(b"Return-Path:")
    assert b"Subject: Second proposal" in messages[1]


def test_should_return_empty_tuple_when_no_byte_message_boundary_exists() -> None:
    assert split_fraudulent_email_corpus_message_bytes(b"plain text without email headers") == ()


def test_should_prepare_fraudulent_corpus_message_sample() -> None:
    sample = prepare_fraudulent_email_corpus_message(
        raw_message=_sample_message("First proposal", "https://example.net/reply"),
        source_id="message-00001",
    )

    assert sample.source == FRAUDULENT_EMAIL_CORPUS_SOURCE
    assert sample.source_id == "message-00001"
    assert sample.source_uri == FRAUDULENT_EMAIL_CORPUS_SOURCE_URI
    assert sample.original_label == FRAUDULENT_EMAIL_CORPUS_ORIGINAL_LABEL
    assert sample.normalized_label == NORMALIZED_LABEL_SUSPICIOUS
    assert sample.subject == "First proposal"
    assert sample.body_text == "Please reply at https://example.net/reply."
    assert sample.sender_domain == "example.net"
    assert sample.urls == ("https://example.net/reply",)
    assert sample.attachment_filenames == ()
    assert sample.raw_available is True
    assert sample.metadata == {"original_label": "fraud"}


def test_should_build_stable_sample_id_for_same_input() -> None:
    first_sample = prepare_fraudulent_email_corpus_message(
        raw_message=_sample_message("First proposal", "https://example.net/reply"),
        source_id="message-00001",
    )
    second_sample = prepare_fraudulent_email_corpus_message(
        raw_message=_sample_message("First proposal", "https://example.net/reply"),
        source_id="message-00001",
    )

    assert first_sample.sample_id == second_sample.sample_id


def test_should_prepare_non_utf8_message_without_replacement_decoding() -> None:
    sample = prepare_fraudulent_email_corpus_message(
        raw_message=_latin1_sample_message_bytes(),
        source_id="message-00002",
    )

    assert sample.subject == "Oferta especial"
    assert sample.body_text == "Transferencia especial para caf\u00e9."


def test_should_prepare_message_with_non_standard_charset() -> None:
    sample = prepare_fraudulent_email_corpus_message(
        raw_message=_non_standard_charset_message_bytes(b"ansi"),
        source_id="message-00003",
    )

    assert sample.subject == "Oferta especial"
    assert sample.body_text == "Transferencia especial para caf\u00e9."


def test_should_prepare_message_with_invalid_charset() -> None:
    sample = prepare_fraudulent_email_corpus_message(
        raw_message=_non_standard_charset_message_bytes(b"iso-4470lgm1879-728jaagth"),
        source_id="message-00004",
    )

    assert sample.subject == "Oferta especial"
    assert sample.body_text == "Transferencia especial para caf\u00e9."


def _sample_corpus_text() -> str:
    return "\n".join(
        [
            "From r Wed Jan 01 00:00:00 2001",
            _sample_message("First proposal", "https://example.net/reply"),
            "",
            "From r Thu Jan 02 00:00:00 2001",
            _sample_message("Second proposal", "https://example.org/reply"),
        ]
    )


def _sample_message(subject: str, url: str) -> str:
    return "\n".join(
        [
            "Return-Path: <sender@example.net>",
            "From: Sender <sender@example.net>",
            "Reply-To: Sender <reply@example.net>",
            "To: recipient@example.com",
            f"Subject: {subject}",
            "Content-Type: text/plain; charset=utf-8",
            "",
            f"Please reply at {url}.",
        ]
    )


def _latin1_sample_message_bytes() -> bytes:
    return b"\n".join(
        [
            b"Return-Path: <sender@example.net>",
            b"From: Sender <sender@example.net>",
            b"Subject: Oferta especial",
            b"Content-Type: text/plain; charset=iso-8859-1",
            b"",
            b"Transferencia especial para caf\xe9.",
        ]
    )


def _non_standard_charset_message_bytes(charset: bytes) -> bytes:
    return b"\n".join(
        [
            b"Return-Path: <sender@example.net>",
            b"From: Sender <sender@example.net>",
            b"Subject: Oferta especial",
            b"Content-Type: text/plain; charset=" + charset,
            b"",
            b"Transferencia especial para caf\xe9.",
        ]
    )
