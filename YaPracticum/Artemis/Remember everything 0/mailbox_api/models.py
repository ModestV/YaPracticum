from django.core.validators import EmailValidator
from django.db import models


class UserAccount(models.Model):
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    display_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["email"]

    def __str__(self) -> str:
        return self.email


class Message(models.Model):
    sender = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    recipient = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.subject} ({self.sender} -> {self.recipient})"


class MailboxEntry(models.Model):
    class Direction(models.TextChoices):
        INCOMING = "incoming", "Incoming"
        OUTGOING = "outgoing", "Outgoing"

    class Folder(models.TextChoices):
        INBOX = "inbox", "Inbox"
        OUTBOX = "outbox", "Outbox"
        ARCHIVE = "archive", "Archive"
        TRASH = "trash", "Trash"

    owner = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name="mailbox_entries",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="mailbox_entries",
    )
    direction = models.CharField(max_length=10, choices=Direction.choices)
    folder = models.CharField(max_length=10, choices=Folder.choices)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-message__created_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "message", "direction"],
                name="unique_mailbox_entry_per_owner_direction",
            )
        ]

    def __str__(self) -> str:
        return f"{self.owner} | {self.direction} | {self.folder}"
