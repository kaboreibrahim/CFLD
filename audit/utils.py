from decimal import Decimal

from django.forms.models import model_to_dict
from django.utils import timezone

from .context import get_current_request


SENSITIVE_KEYS = {"password", "secret", "token", "api_key", "csrfmiddlewaretoken"}


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR")


def get_location_from_request(request):
    city = request.META.get("HTTP_CF_IPCITY") or request.META.get("HTTP_X_CITY")
    region = request.META.get("HTTP_CF_REGION") or request.META.get("HTTP_X_REGION")
    country = (
        request.META.get("HTTP_CF_IPCOUNTRY")
        or request.META.get("HTTP_X_COUNTRY")
        or request.META.get("GEOIP_COUNTRY_NAME")
    )
    parts = [part for part in (city, region, country) if part]
    if parts:
        return ", ".join(parts)

    ip = get_client_ip(request)
    if ip in {"127.0.0.1", "::1"}:
        return "Localhost"
    return None


def build_request_metadata(request):
    return {
        "ip_address": get_client_ip(request),
        "localisation": get_location_from_request(request),
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        "url": request.get_full_path()[:500],
        "http_method": request.method,
    }


def get_request_metadata(request=None):
    request = request or get_current_request()
    if not request:
        return {}
    return getattr(request, "audit_metadata", None) or build_request_metadata(request)


def get_request_user(request=None):
    request = request or get_current_request()
    if not request:
        return None
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        return user
    return None


def username_for(user=None, fallback="Anonyme"):
    if not user:
        return fallback
    getter = getattr(user, "get_username", None)
    return getter() if getter else str(user)


def to_json_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "name"):
        return value.name
    return str(value)


def model_snapshot(instance):
    data = model_to_dict(instance)
    clean = {}
    for key, value in data.items():
        if any(secret in key.lower() for secret in SENSITIVE_KEYS):
            clean[key] = "***"
        elif isinstance(value, (list, tuple)):
            clean[key] = [to_json_value(item) for item in value]
        else:
            clean[key] = to_json_value(value)
    return clean


def diff_snapshots(old, new):
    if not old:
        return None, new
    old_diff = {}
    new_diff = {}
    for key in sorted(set(old) | set(new)):
        if old.get(key) != new.get(key):
            old_diff[key] = old.get(key)
            new_diff[key] = new.get(key)
    return old_diff or None, new_diff or None


def create_audit_log(
    *,
    action,
    model_name,
    description,
    request=None,
    user=None,
    object_id=None,
    ancienne_valeur=None,
    nouvelle_valeur=None,
    username=None,
):
    from .models import AuditLog

    user = user or get_request_user(request)
    metadata = get_request_metadata(request)
    return AuditLog.objects.create(
        user=user,
        username=username or username_for(user),
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id is not None else None,
        description=description,
        ancienne_valeur=ancienne_valeur,
        nouvelle_valeur=nouvelle_valeur,
        ip_address=metadata.get("ip_address"),
        localisation=metadata.get("localisation"),
        user_agent=metadata.get("user_agent"),
        url=metadata.get("url", ""),
        http_method=metadata.get("http_method", ""),
    )


def log_view(request, model_name, description, object_id=None):
    from .models import AuditLog

    return create_audit_log(
        action=AuditLog.ACTION_VIEW,
        model_name=model_name,
        object_id=object_id,
        description=description,
        request=request,
    )


def log_download(request, model_name, description, object_id=None, action=None):
    from .models import AuditLog

    return create_audit_log(
        action=action or AuditLog.ACTION_DOWNLOAD,
        model_name=model_name,
        object_id=object_id,
        description=description,
        request=request,
    )


def today():
    return timezone.localdate()

