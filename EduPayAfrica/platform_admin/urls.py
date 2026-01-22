from django.urls import path

from . import views

app_name = "platform_admin"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("institutions/", views.institutions, name="institutions"),
    path("demo-requests/", views.demo_requests, name="demo_requests"),
    path("users/", views.user_oversight, name="users"),
    path("settings/", views.settings_view, name="settings"),
    path("audit-logs/", views.audit_logs, name="audit_logs"),
]
