from .models import MailboxEntry, Message


def serialize_message(entry: MailboxEntry, include_body: bool = False) -> dict:
    message: Message = entry.message
    payload = {
        "message_id": message.id,
        "entry_id": entry.id,
        "owner_email": entry.owner.email,
        "direction": entry.direction,
        "folder": entry.folder,
        "is_read": entry.is_read,
        "read_at": entry.read_at.isoformat() if entry.read_at else None,
        "subject": message.subject,
        "sender_email": message.sender.email,
        "recipient_email": message.recipient.email,
        "created_at": message.created_at.isoformat(),
        "updated_at": entry.updated_at.isoformat(),
    }
    if include_body:
        payload["body"] = message.body
    return payload
