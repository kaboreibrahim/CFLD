from django.apps import apps
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import AuditLog
from .utils import (
    create_audit_log,
    diff_snapshots,
    model_snapshot,
    username_for,
)


_old_values = {}


def watched_models():
    models = set(apps.get_app_config("payments").get_models())
    models.add(apps.get_model(settings.AUTH_USER_MODEL))
    return models


def should_watch(sender):
    return sender in watched_models() and sender is not AuditLog


def model_label(sender):
    return sender._meta.verbose_name.title()


@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    if not should_watch(sender) or not instance.pk:
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    _old_values[(sender, instance.pk)] = model_snapshot(old_instance)


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if not should_watch(sender):
        return

    new_value = model_snapshot(instance)
    old_value = None
    if not created:
        old_value = _old_values.pop((sender, instance.pk), None)
        old_value, new_value = diff_snapshots(old_value, new_value)
        if not old_value and not new_value:
            return

    action = AuditLog.ACTION_CREATE if created else AuditLog.ACTION_UPDATE
    verb = "Creation" if created else "Modification"
    create_audit_log(
        action=action,
        model_name=sender.__name__,
        object_id=instance.pk,
        description=f"{verb} de {model_label(sender)} : {instance}.",
        ancienne_valeur=old_value,
        nouvelle_valeur=new_value,
    )


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if not should_watch(sender):
        return
    create_audit_log(
        action=AuditLog.ACTION_DELETE,
        model_name=sender.__name__,
        object_id=instance.pk,
        description=f"Suppression de {model_label(sender)} : {instance}.",
        ancienne_valeur=model_snapshot(instance),
    )


@receiver(user_logged_in)
def audit_login(sender, request, user, **kwargs):
    create_audit_log(
        action=AuditLog.ACTION_LOGIN,
        model_name=user.__class__.__name__,
        object_id=user.pk,
        user=user,
        request=request,
        description=f"{username_for(user)} s'est connecte a l'application.",
    )


@receiver(user_logged_out)
def audit_logout(sender, request, user, **kwargs):
    create_audit_log(
        action=AuditLog.ACTION_LOGOUT,
        model_name=user.__class__.__name__ if user else "Utilisateur",
        object_id=getattr(user, "pk", None),
        user=user,
        request=request,
        description=f"{username_for(user)} s'est deconnecte.",
    )


@receiver(user_login_failed)
def audit_failed_login(sender, credentials, request, **kwargs):
    username = (
        credentials.get("username")
        or credentials.get("email")
        or credentials.get("login")
        or "identifiant inconnu"
    )
    create_audit_log(
        action=AuditLog.ACTION_FAILED_LOGIN,
        model_name="Utilisateur",
        request=request,
        username=str(username),
        description=f"Tentative de connexion echouee avec l'identifiant {username}.",
    )

