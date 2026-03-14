import json

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from .models import MailboxEntry


class MailboxApiTests(TestCase):
    def test_root_redirects_to_mailbox_page(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("mailbox-home"))

    def test_mailbox_page_is_available(self) -> None:
        response = self.client.get(reverse("mailbox-home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, settings.DEMO_MAILBOX_EMAIL)

    def test_compose_page_is_available(self) -> None:
        response = self.client.get(reverse("mailbox-compose"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "name=\"action\"")

    def test_web_send_message_creates_outgoing_entry_for_demo_user(self) -> None:
        response = self.client.post(
            reverse("mailbox-compose"),
            data={
                "recipient_email": "bob@example.com",
                "subject": "UI hello",
                "body": "Sent from the web form.",
                "action": "send",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            MailboxEntry.objects.filter(
                owner__email=settings.DEMO_MAILBOX_EMAIL,
                direction=MailboxEntry.Direction.OUTGOING,
                folder=MailboxEntry.Folder.OUTBOX,
                message__subject="UI hello",
            ).exists()
        )

    def test_write_to_self_creates_unread_incoming_only(self) -> None:
        response = self.client.post(
            reverse("mailbox-compose"),
            data={
                "recipient_email": "",
                "subject": "Note to self",
                "body": "Remember to remember.",
                "action": "self",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            MailboxEntry.objects.filter(message__subject="Note to self").count(),
            1,
        )
        self.assertTrue(
            MailboxEntry.objects.filter(
                owner__email=settings.DEMO_MAILBOX_EMAIL,
                direction=MailboxEntry.Direction.INCOMING,
                folder=MailboxEntry.Folder.INBOX,
                is_read=False,
                message__subject="Note to self",
            ).exists()
        )

    def test_send_message_creates_inbox_and_outbox_entries(self) -> None:
        response = self.client.post(
            reverse("send-message"),
            data=json.dumps(
                {
                    "sender_email": "alice@example.com",
                    "recipient_email": "bob@example.com",
                    "subject": "Hello",
                    "body": "How are you?",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(MailboxEntry.objects.count(), 2)
        self.assertTrue(
            MailboxEntry.objects.filter(
                owner__email="bob@example.com",
                direction=MailboxEntry.Direction.INCOMING,
                folder=MailboxEntry.Folder.INBOX,
                is_read=False,
            ).exists()
        )

    def test_get_message_marks_incoming_as_read(self) -> None:
        send_response = self.client.post(
            reverse("send-message"),
            data=json.dumps(
                {
                    "sender_email": "alice@example.com",
                    "recipient_email": "bob@example.com",
                    "subject": "Hello",
                    "body": "Please read this.",
                }
            ),
            content_type="application/json",
        )
        message_id = send_response.json()["message_id"]

        response = self.client.get(
            reverse("message-detail", kwargs={"message_id": message_id}),
            data={"owner_email": "bob@example.com"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["is_read"])

    def test_mailbox_detail_marks_demo_incoming_as_read(self) -> None:
        self.client.post(
            reverse("mailbox-compose"),
            data={
                "subject": "Unopened note",
                "body": "Read me later.",
                "action": "self",
            },
        )
        entry = MailboxEntry.objects.get(message__subject="Unopened note")

        response = self.client.get(reverse("mailbox-entry-detail", kwargs={"entry_id": entry.id}))

        self.assertEqual(response.status_code, 200)
        entry.refresh_from_db()
        self.assertTrue(entry.is_read)

    def test_move_message_to_archive(self) -> None:
        send_response = self.client.post(
            reverse("send-message"),
            data=json.dumps(
                {
                    "sender_email": "alice@example.com",
                    "recipient_email": "bob@example.com",
                    "subject": "Archive me",
                    "body": "Important message.",
                }
            ),
            content_type="application/json",
        )
        message_id = send_response.json()["message_id"]

        response = self.client.post(
            reverse("move-message", kwargs={"message_id": message_id}),
            data=json.dumps({"owner_email": "bob@example.com", "target_folder": "archive"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["folder"], "archive")

    def test_web_move_and_delete_actions_work(self) -> None:
        self.client.post(
            reverse("mailbox-compose"),
            data={
                "recipient_email": "bob@example.com",
                "subject": "Move me",
                "body": "Please archive me.",
                "action": "send",
            },
        )
        entry = MailboxEntry.objects.get(
            owner__email=settings.DEMO_MAILBOX_EMAIL,
            message__subject="Move me",
        )

        move_response = self.client.post(
            reverse("mailbox-entry-move", kwargs={"entry_id": entry.id}),
            data={"target_folder": "archive"},
        )
        self.assertEqual(move_response.status_code, 302)
        entry.refresh_from_db()
        self.assertEqual(entry.folder, MailboxEntry.Folder.ARCHIVE)

        delete_response = self.client.post(
            reverse("mailbox-entry-delete", kwargs={"entry_id": entry.id}),
        )
        self.assertEqual(delete_response.status_code, 302)
        self.assertFalse(MailboxEntry.objects.filter(id=entry.id).exists())

    def test_delete_removes_only_owner_copy(self) -> None:
        send_response = self.client.post(
            reverse("send-message"),
            data=json.dumps(
                {
                    "sender_email": "alice@example.com",
                    "recipient_email": "bob@example.com",
                    "subject": "Delete me",
                    "body": "Temporary message.",
                }
            ),
            content_type="application/json",
        )
        message_id = send_response.json()["message_id"]

        response = self.client.delete(
            reverse("message-detail", kwargs={"message_id": message_id}),
            data=json.dumps({"owner_email": "bob@example.com"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(MailboxEntry.objects.count(), 1)
