from django.urls import path

from .views import (
    ComposeMessagePageView,
    MailboxEntryDeletePageView,
    MailboxEntryDetailPageView,
    MailboxEntryMovePageView,
    MailboxPageView,
)


urlpatterns = [
    path("mailbox/", MailboxPageView.as_view(), name="mailbox-home"),
    path("mailbox/compose/", ComposeMessagePageView.as_view(), name="mailbox-compose"),
    path("mailbox/<int:entry_id>/", MailboxEntryDetailPageView.as_view(), name="mailbox-entry-detail"),
    path("mailbox/<int:entry_id>/move/", MailboxEntryMovePageView.as_view(), name="mailbox-entry-move"),
    path("mailbox/<int:entry_id>/delete/", MailboxEntryDeletePageView.as_view(), name="mailbox-entry-delete"),
]
