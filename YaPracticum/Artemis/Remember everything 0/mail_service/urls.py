from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="mailbox-home", permanent=False)),
    path("", include("mailbox_api.web_urls")),
    path("admin/", admin.site.urls),
    path("api/", include("mailbox_api.urls")),
]
