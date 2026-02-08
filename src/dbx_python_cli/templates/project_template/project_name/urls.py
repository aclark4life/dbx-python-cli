from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView


urlpatterns = [
    path("admin/", admin.site.urls),
    # This will serve the built-in welcome template at /
    path(
        "",
        TemplateView.as_view(template_name="default_urlconf.html"),
        name="default_urlconf",
    ),
] + debug_toolbar_urls()
