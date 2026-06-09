import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=255)),
                ("action", models.CharField(choices=[("LOGIN", "Connexion"), ("LOGOUT", "Deconnexion"), ("FAILED_LOGIN", "Echec de connexion"), ("CREATE", "Creation"), ("UPDATE", "Modification"), ("DELETE", "Suppression"), ("VIEW", "Consultation"), ("DOWNLOAD", "Telechargement"), ("PRINT", "Impression"), ("EXPORT_EXCEL", "Export Excel"), ("EXPORT_PDF", "Export PDF")], db_index=True, max_length=100)),
                ("model_name", models.CharField(db_index=True, max_length=255)),
                ("object_id", models.CharField(blank=True, max_length=255, null=True)),
                ("description", models.TextField()),
                ("ancienne_valeur", models.JSONField(blank=True, null=True)),
                ("nouvelle_valeur", models.JSONField(blank=True, null=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("localisation", models.CharField(blank=True, max_length=255, null=True)),
                ("user_agent", models.TextField(blank=True, null=True)),
                ("url", models.CharField(blank=True, default="", max_length=500)),
                ("http_method", models.CharField(blank=True, default="", max_length=10)),
                ("date_action", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Journal d'audit",
                "verbose_name_plural": "Journaux d'audit",
                "ordering": ["-date_action"],
                "indexes": [
                    models.Index(fields=["date_action"], name="idx_audit_date_action"),
                    models.Index(fields=["action", "model_name"], name="idx_audit_action_model"),
                    models.Index(fields=["username"], name="idx_audit_username"),
                    models.Index(fields=["ip_address"], name="idx_audit_ip"),
                ],
            },
        ),
    ]

