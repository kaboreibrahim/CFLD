from django.contrib import admin
from django.db.models import Count
from django.utils import timezone

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        "date_action",
        "username",
        "action",
        "model_name",
        "object_id",
        "ip_address",
        "localisation",
    ]
    list_filter = ["action", "model_name", "ip_address", "date_action", "user"]
    search_fields = ["username", "action", "description", "model_name", "object_id"]
    readonly_fields = [
        "user",
        "username",
        "action",
        "model_name",
        "object_id",
        "description",
        "ancienne_valeur",
        "nouvelle_valeur",
        "ip_address",
        "localisation",
        "user_agent",
        "url",
        "http_method",
        "date_action",
    ]
    date_hierarchy = "date_action"
    ordering = ["-date_action"]
    change_list_template = "admin/audit/auditlog/change_list.html"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return bool(request.user and request.user.is_superuser)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return bool(request.user and request.user.is_superuser)

    def changelist_view(self, request, extra_context=None):
        today = timezone.localdate()
        qs = self.get_queryset(request)
        extra_context = extra_context or {}
        extra_context["audit_stats"] = {
            "logins_today": qs.filter(action=AuditLog.ACTION_LOGIN, date_action__date=today).count(),
            "creates": qs.filter(action=AuditLog.ACTION_CREATE).count(),
            "updates": qs.filter(action=AuditLog.ACTION_UPDATE).count(),
            "deletes": qs.filter(action=AuditLog.ACTION_DELETE).count(),
            "top_users": qs.values("username").annotate(total=Count("id")).order_by("-total")[:5],
            "actions": qs.values("action").annotate(total=Count("id")).order_by("-total"),
        }
        return super().changelist_view(request, extra_context=extra_context)

