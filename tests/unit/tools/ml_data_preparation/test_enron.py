from tools.ml_data_preparation.enron import (
    ENRON_ORIGINAL_LABEL,
    ENRON_SOURCE,
    ENRON_SOURCE_URI,
    NORMALIZED_LABEL_BENIGN,
    enron_source_id_from_path,
    parse_enron_relative_path,
    prepare_enron_email,
)


def test_should_parse_enron_archive_member_path() -> None:
    mailbox_user, folder = parse_enron_relative_path("maildir/user-a/inbox/1.")

    assert mailbox_user == "user-a"
    assert folder == "inbox"


def test_should_parse_nested_enron_archive_member_path() -> None:
    mailbox_user, folder = parse_enron_relative_path("maildir/user-a/discussion_threads/project/2.")

    assert mailbox_user == "user-a"
    assert folder == "discussion_threads/project"


def test_should_return_empty_metadata_for_unexpected_archive_member_path() -> None:
    assert parse_enron_relative_path("unexpected") == ("", "")


def test_should_build_source_id_from_path(tmp_path) -> None:
    input_dir = tmp_path / "maildir"
    email_path = input_dir / "user-a" / "inbox" / "1."
    email_path.parent.mkdir(parents=True)
    email_path.write_bytes(b"body")

    assert enron_source_id_from_path(input_dir=input_dir, email_path=email_path) == "user-a/inbox/1."


def test_should_prepare_enron_email_sample() -> None:
    sample = prepare_enron_email(
        raw_email=_sample_email_bytes(),
        source_id="user-a/inbox/1.",
        relative_path="user-a/inbox/1.",
    )

    assert sample.source == ENRON_SOURCE
    assert sample.source_id == "user-a/inbox/1."
    assert sample.source_uri == ENRON_SOURCE_URI
    assert sample.original_label == ENRON_ORIGINAL_LABEL
    assert sample.normalized_label == NORMALIZED_LABEL_BENIGN
    assert sample.subject == "Project update"
    assert sample.body_text == "Please review the planning document at https://example.com/doc."
    assert sample.sender_domain == "example.com"
    assert sample.urls == ("https://example.com/doc",)
    assert sample.attachment_filenames == ()
    assert sample.raw_available is True
    assert sample.metadata == {
        "relative_path": "user-a/inbox/1.",
        "mailbox_user": "user-a",
        "folder": "inbox",
        "original_label": "benign",
    }


def test_should_build_stable_sample_id_for_same_input() -> None:
    first_sample = prepare_enron_email(
        raw_email=_sample_email_bytes(),
        source_id="user-a/inbox/1.",
        relative_path="user-a/inbox/1.",
    )
    second_sample = prepare_enron_email(
        raw_email=_sample_email_bytes(),
        source_id="user-a/inbox/1.",
        relative_path="user-a/inbox/1.",
    )

    assert first_sample.sample_id == second_sample.sample_id


def _sample_email_bytes() -> bytes:
    return "\r\n".join(
        [
            "From: Project Team <project@example.com>",
            "Subject: Project update",
            "Content-Type: text/plain; charset=utf-8",
            "",
            "Please review the planning document at https://example.com/doc.",
        ]
    ).encode("utf-8")
