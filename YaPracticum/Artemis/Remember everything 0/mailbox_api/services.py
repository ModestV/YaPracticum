from django.db import transaction
from django.utils import timezone

from .models import MailboxEntry, Message, UserAccount


def get_or_create_user(email: str, display_name: str = "") -> UserAccount:
    normalized_email = email.strip().lower()
    user, _ = UserAccount.objects.get_or_create(email=normalized_email)
    if display_name and user.display_name != display_name:
        user.display_name = display_name
        user.save(update_fields=["display_name"])
    return user


@transaction.atomic
def send_message(*, sender_email: str, recipient_email: str, subject: str, body: str) -> Message:
    sender = get_or_create_user(sender_email)
    recipient = get_or_create_user(recipient_email)

    message = Message.objects.create(
        sender=sender,
        recipient=recipient,
        subject=subject.strip(),
        body=body.strip(),
    )

    MailboxEntry.objects.create(
        owner=recipient,
        message=message,
        direction=MailboxEntry.Direction.INCOMING,
        folder=MailboxEntry.Folder.INBOX,
        is_read=False,
    )
    MailboxEntry.objects.create(
        owner=sender,
        message=message,
        direction=MailboxEntry.Direction.OUTGOING,
        folder=MailboxEntry.Folder.OUTBOX,
        is_read=True,
        read_at=timezone.now(),
    )
    return message


@transaction.atomic
def create_incoming_self_note(*, owner_email: str, subject: str, body: str) -> MailboxEntry:
    owner = get_or_create_user(owner_email)
    message = Message.objects.create(
        sender=owner,
        recipient=owner,
        subject=subject.strip(),
        body=body.strip(),
    )
    return MailboxEntry.objects.create(
        owner=owner,
        message=message,
        direction=MailboxEntry.Direction.INCOMING,
        folder=MailboxEntry.Folder.INBOX,
        is_read=False,
    )


def mark_as_read(entry: MailboxEntry) -> MailboxEntry:
    if not entry.is_read:
        entry.is_read = True
        entry.read_at = timezone.now()
        entry.save(update_fields=["is_read", "read_at", "updated_at"])
    return entry


def move_entry(entry: MailboxEntry, target_folder: str) -> MailboxEntry:
    allowed_targets = {
        MailboxEntry.Direction.INCOMING: {
            MailboxEntry.Folder.INBOX,
            MailboxEntry.Folder.ARCHIVE,
            MailboxEntry.Folder.TRASH,
        },
        MailboxEntry.Direction.OUTGOING: {
            MailboxEntry.Folder.OUTBOX,
            MailboxEntry.Folder.ARCHIVE,
            MailboxEntry.Folder.TRASH,
        },
    }
    if target_folder not in allowed_targets[entry.direction]:
        raise ValueError("Target folder is not allowed for this message direction.")

    entry.folder = target_folder
    entry.save(update_fields=["folder", "updated_at"])
    return entry


@transaction.atomic
def delete_entry(entry: MailboxEntry) -> None:
    message = entry.message
    entry.delete()
    if not message.mailbox_entries.exists():
        message.delete()
