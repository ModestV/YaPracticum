import json

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Count, QuerySet
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from .forms import ComposeMessageForm
from .models import MailboxEntry, UserAccount
from .serializers import serialize_message
from .services import (
    create_incoming_self_note,
    delete_entry,
    get_or_create_user,
    mark_as_read,
    move_entry,
    send_message,
)


def parse_json_body(request: HttpRequest) -> dict:
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError as exc:
        raise ValidationError("Request body must be valid JSON.") from exc


def validate_email_field(value: str, field_name: str) -> str:
    candidate = (value or "").strip().lower()
    if not candidate:
        raise ValidationError({field_name: "This field is required."})
    try:
        validate_email(candidate)
    except ValidationError as exc:
        raise ValidationError({field_name: "Enter a valid email address."}) from exc
    return candidate


def get_entry_for_owner(message_id: int, owner_email: str) -> MailboxEntry:
    normalized_email = validate_email_field(owner_email, "owner_email")
    return get_object_or_404(
        MailboxEntry.objects.select_related("message", "message__sender", "message__recipient", "owner"),
        message_id=message_id,
        owner__email=normalized_email,
    )


def get_demo_user() -> UserAccount:
    return get_or_create_user(
        settings.DEMO_MAILBOX_EMAIL,
        display_name=settings.DEMO_MAILBOX_NAME,
    )


def get_demo_mailbox_queryset() -> QuerySet[MailboxEntry]:
    demo_user = get_demo_user()
    return MailboxEntry.objects.select_related(
        "owner",
        "message",
        "message__sender",
        "message__recipient",
    ).filter(owner=demo_user)


def get_demo_entry(entry_id: int) -> MailboxEntry:
    return get_object_or_404(get_demo_mailbox_queryset(), id=entry_id)


def get_active_folder(folder_name: str | None) -> str:
    if folder_name in MailboxEntry.Folder.values:
        return folder_name
    return MailboxEntry.Folder.INBOX


def get_folder_label(folder_name: str) -> str:
    labels = {
        MailboxEntry.Folder.INBOX: "Входящие",
        MailboxEntry.Folder.OUTBOX: "Исходящие",
        MailboxEntry.Folder.ARCHIVE: "Архив",
        MailboxEntry.Folder.TRASH: "Корзина",
    }
    return labels[folder_name]


def get_quick_actions(entry: MailboxEntry) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    base_folder = (
        MailboxEntry.Folder.INBOX
        if entry.direction == MailboxEntry.Direction.INCOMING
        else MailboxEntry.Folder.OUTBOX
    )

    if entry.folder != MailboxEntry.Folder.ARCHIVE:
        actions.append({"value": MailboxEntry.Folder.ARCHIVE, "label": "В архив"})
    if entry.folder != MailboxEntry.Folder.TRASH:
        actions.append({"value": MailboxEntry.Folder.TRASH, "label": "В корзину"})
    if entry.folder != base_folder:
        label = "Вернуть во входящие" if base_folder == MailboxEntry.Folder.INBOX else "Вернуть в исходящие"
        actions.append({"value": base_folder, "label": label})
    return actions


def decorate_entry(entry: MailboxEntry) -> MailboxEntry:
    entry.quick_actions = get_quick_actions(entry)
    entry.folder_label = get_folder_label(entry.folder)
    entry.direction_label = "Входящее" if entry.direction == MailboxEntry.Direction.INCOMING else "Исходящее"
    return entry


def build_mailbox_base_context(*, active_folder: str) -> dict:
    demo_user = get_demo_user()
    counts_by_folder = {
        row["folder"]: row["total"]
        for row in get_demo_mailbox_queryset().values("folder").annotate(total=Count("id"))
    }
    folder_order = [
        MailboxEntry.Folder.INBOX,
        MailboxEntry.Folder.OUTBOX,
        MailboxEntry.Folder.ARCHIVE,
        MailboxEntry.Folder.TRASH,
    ]
    return {
        "demo_user": demo_user,
        "active_folder": active_folder,
        "active_folder_label": get_folder_label(active_folder),
        "folder_links": [
            {
                "value": folder,
                "label": get_folder_label(folder),
                "count": counts_by_folder.get(folder, 0),
                "is_active": folder == active_folder,
            }
            for folder in folder_order
        ],
    }


class MailboxPageView(View):
    template_name = "mailbox_api/mailbox.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        active_folder = get_active_folder(request.GET.get("folder"))
        entries = [
            decorate_entry(entry)
            for entry in get_demo_mailbox_queryset()
            .filter(folder=active_folder)
            .order_by("is_read", "-message__created_at")
        ]
        context = build_mailbox_base_context(active_folder=active_folder)
        context.update({"entries": entries})
        return render(request, self.template_name, context)


class ComposeMessagePageView(View):
    template_name = "mailbox_api/compose.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        form = ComposeMessageForm(
            initial={
                "recipient_email": request.GET.get("recipient_email", ""),
                "subject": request.GET.get("subject", ""),
            }
        )
        context = build_mailbox_base_context(active_folder=MailboxEntry.Folder.OUTBOX)
        context.update({"form": form})
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = ComposeMessageForm(request.POST)
        action = request.POST.get("action", "send")

        if form.is_valid():
            subject = form.cleaned_data["subject"]
            body = form.cleaned_data["body"]
            demo_email = settings.DEMO_MAILBOX_EMAIL

            if action == "self":
                entry = create_incoming_self_note(
                    owner_email=demo_email,
                    subject=subject,
                    body=body,
                )
                messages.success(request, "Письмо тихонько положено само себе во входящие.")
                return redirect("mailbox-entry-detail", entry_id=entry.id)

            recipient_email = form.cleaned_data["recipient_email"]
            if not recipient_email:
                form.add_error("recipient_email", "Укажите адрес получателя.")
            else:
                message = send_message(
                    sender_email=demo_email,
                    recipient_email=recipient_email,
                    subject=subject,
                    body=body,
                )
                entry = message.mailbox_entries.select_related(
                    "owner",
                    "message__sender",
                    "message__recipient",
                ).get(
                    owner__email=demo_email,
                    direction=MailboxEntry.Direction.OUTGOING,
                )
                messages.success(request, "Письмо отправлено в мир и сохранено в исходящих.")
                return redirect("mailbox-entry-detail", entry_id=entry.id)

        context = build_mailbox_base_context(active_folder=MailboxEntry.Folder.OUTBOX)
        context.update({"form": form})
        return render(request, self.template_name, context, status=400)


class MailboxEntryDetailPageView(View):
    template_name = "mailbox_api/message_detail.html"

    def get(self, request: HttpRequest, entry_id: int) -> HttpResponse:
        entry = decorate_entry(get_demo_entry(entry_id))
        if entry.direction == MailboxEntry.Direction.INCOMING:
            entry = decorate_entry(mark_as_read(entry))

        context = build_mailbox_base_context(active_folder=entry.folder)
        context.update({"entry": entry})
        return render(request, self.template_name, context)


class MailboxEntryMovePageView(View):
    def post(self, request: HttpRequest, entry_id: int) -> HttpResponse:
        entry = get_demo_entry(entry_id)
        target_folder = (request.POST.get("target_folder") or "").strip().lower()

        if target_folder not in MailboxEntry.Folder.values:
            messages.error(request, "Не удалось понять, куда перекладывать письмо.")
            return redirect("mailbox-home")

        try:
            move_entry(entry, target_folder)
            messages.success(request, f"Письмо переехало в папку «{get_folder_label(target_folder)}».")
        except ValueError:
            messages.error(request, "Эту бумажку нельзя положить в выбранную папку.")

        next_url = request.POST.get("next")
        if next_url:
            return redirect(next_url)
        return redirect(f"{reverse('mailbox-home')}?folder={target_folder}")


class MailboxEntryDeletePageView(View):
    def post(self, request: HttpRequest, entry_id: int) -> HttpResponse:
        entry = get_demo_entry(entry_id)
        delete_entry(entry)
        messages.success(request, "Письмо удалено из этого ящика.")
        return redirect(f"{reverse('mailbox-home')}?folder={MailboxEntry.Folder.TRASH}")


class SendMessageView(View):
    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            payload = parse_json_body(request)
            sender_email = validate_email_field(payload.get("sender_email"), "sender_email")
            recipient_email = validate_email_field(payload.get("recipient_email"), "recipient_email")
            subject = (payload.get("subject") or "").strip()
            body = (payload.get("body") or "").strip()
            if not subject:
                raise ValidationError({"subject": "This field is required."})
            if not body:
                raise ValidationError({"body": "This field is required."})

            message = send_message(
                sender_email=sender_email,
                recipient_email=recipient_email,
                subject=subject,
                body=body,
            )
            entry = message.mailbox_entries.select_related(
                "owner", "message__sender", "message__recipient"
            ).get(owner__email=sender_email, direction=MailboxEntry.Direction.OUTGOING)
            return JsonResponse(serialize_message(entry, include_body=True), status=201)
        except ValidationError as exc:
            return JsonResponse({"errors": exc.message_dict if hasattr(exc, "message_dict") else exc.messages}, status=400)


class MessageListView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        try:
            owner_email = validate_email_field(request.GET.get("owner_email"), "owner_email")
            folder = (request.GET.get("folder") or "").strip().lower()
            direction = (request.GET.get("direction") or "").strip().lower()

            entries: QuerySet[MailboxEntry] = MailboxEntry.objects.select_related(
                "owner", "message", "message__sender", "message__recipient"
            ).filter(owner__email=owner_email)
            if folder:
                if folder not in MailboxEntry.Folder.values:
                    raise ValidationError({"folder": "Unsupported folder."})
                entries = entries.filter(folder=folder)
            if direction:
                if direction not in MailboxEntry.Direction.values:
                    raise ValidationError({"direction": "Unsupported direction."})
                entries = entries.filter(direction=direction)

            return JsonResponse({"results": [serialize_message(entry) for entry in entries]})
        except ValidationError as exc:
            return JsonResponse({"errors": exc.message_dict if hasattr(exc, "message_dict") else exc.messages}, status=400)


class MessageDetailView(View):
    def get(self, request: HttpRequest, message_id: int) -> JsonResponse:
        try:
            owner_email = request.GET.get("owner_email")
            entry = get_entry_for_owner(message_id, owner_email)
            if entry.direction == MailboxEntry.Direction.INCOMING:
                entry = mark_as_read(entry)
            return JsonResponse(serialize_message(entry, include_body=True))
        except Http404:
            return JsonResponse({"errors": {"message": "Message not found for this owner."}}, status=404)
        except ValidationError as exc:
            return JsonResponse({"errors": exc.message_dict if hasattr(exc, "message_dict") else exc.messages}, status=400)

    def delete(self, request: HttpRequest, message_id: int) -> JsonResponse:
        try:
            payload = parse_json_body(request) if request.body else {}
            owner_email = payload.get("owner_email") or request.GET.get("owner_email")
            entry = get_entry_for_owner(message_id, owner_email)
            delete_entry(entry)
            return JsonResponse({}, status=204)
        except Http404:
            return JsonResponse({"errors": {"message": "Message not found for this owner."}}, status=404)
        except ValidationError as exc:
            return JsonResponse({"errors": exc.message_dict if hasattr(exc, "message_dict") else exc.messages}, status=400)


class MoveMessageView(View):
    def post(self, request: HttpRequest, message_id: int) -> JsonResponse:
        try:
            payload = parse_json_body(request)
            owner_email = payload.get("owner_email")
            target_folder = (payload.get("target_folder") or "").strip().lower()
            if target_folder not in MailboxEntry.Folder.values:
                raise ValidationError({"target_folder": "Unsupported folder."})

            entry = get_entry_for_owner(message_id, owner_email)
            entry = move_entry(entry, target_folder)
            return JsonResponse(serialize_message(entry, include_body=True))
        except Http404:
            return JsonResponse({"errors": {"message": "Message not found for this owner."}}, status=404)
        except ValidationError as exc:
            return JsonResponse({"errors": exc.message_dict if hasattr(exc, "message_dict") else exc.messages}, status=400)
        except ValueError as exc:
            return JsonResponse({"errors": {"target_folder": str(exc)}}, status=400)
