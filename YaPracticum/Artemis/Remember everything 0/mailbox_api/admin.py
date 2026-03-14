from django.contrib import admin

from .models import MailboxEntry, Message, UserAccount


@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ("email", "display_name", "created_at")
    search_fields = ("email", "display_name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "sender", "recipient", "created_at")
    search_fields = ("subject", "sender__email", "recipient__email")


@admin.register(MailboxEntry)
class MailboxEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "message", "direction", "folder", "is_read", "updated_at")
    list_filter = ("direction", "folder", "is_read")
    search_fields = ("owner__email", "message__subject")
