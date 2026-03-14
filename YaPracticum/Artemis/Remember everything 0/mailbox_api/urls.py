from django.urls import path

from .views import MessageDetailView, MessageListView, MoveMessageView, SendMessageView


urlpatterns = [
    path("messages/send/", SendMessageView.as_view(), name="send-message"),
    path("messages/", MessageListView.as_view(), name="message-list"),
    path("messages/<int:message_id>/", MessageDetailView.as_view(), name="message-detail"),
    path("messages/<int:message_id>/move/", MoveMessageView.as_view(), name="move-message"),
]
