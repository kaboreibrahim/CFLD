from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    ACTION_LOGIN = "LOGIN"
    ACTION_LOGOUT = "LOGOUT"
    ACTION_FAILED_LOGIN = "FAILED_LOGIN"
    ACTION_CREATE = "CREATE"
    ACTION_UPDATE = "UPDATE"
    ACTION_DELETE = "DELETE"
    ACTION_VIEW = "VIEW"
    ACTION_DOWNLOAD = "DOWNLOAD"
    ACTION_PRINT = "PRINT"
    ACTION_EXPORT_EXCEL = "EXPORT_EXCEL"
    ACTION_EXPORT_PDF = "EXPORT_PDF"

    ACTION_CHOICES = [
        (ACTION_LOGIN, "Connexion"),
        (ACTION_LOGOUT, "Deconnexion"),
        (ACTION_FAILED_LOGIN, "Echec de connexion"),
        (ACTION_CREATE, "Creation"),
        (ACTION_UPDATE, "Modification"),
        (ACTION_DELETE, "Suppression"),
        (ACTION_VIEW, "Consultation"),
        (ACTION_DOWNLOAD, "Telechargement"),
        (ACTION_PRINT, "Impression"),
        (ACTION_EXPORT_EXCEL, "Export Excel"),
        (ACTION_EXPORT_PDF, "Export PDF"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    username = models.CharField(max_length=255)
    action = models.CharField(max_length=100, choices=ACTION_CHOICES, db_index=True)
    model_name = models.CharField(max_length=255, db_index=True)
    object_id = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    ancienne_valeur = models.JSONField(blank=True, null=True)
    nouvelle_valeur = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    localisation = models.CharField(max_length=255, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=500, blank=True, default="")
    http_method = models.CharField(max_length=10, blank=True, default="")
    date_action = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_action"]
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journaux d'audit"
        indexes = [
            models.Index(fields=["date_action"], name="idx_audit_date_action"),
            models.Index(fields=["action", "model_name"], name="idx_audit_action_model"),
            models.Index(fields=["username"], name="idx_audit_username"),
            models.Index(fields=["ip_address"], name="idx_audit_ip"),
        ]

    def __str__(self):
        return f"{self.date_action:%Y-%m-%d %H:%M} - {self.username} - {self.action}"

