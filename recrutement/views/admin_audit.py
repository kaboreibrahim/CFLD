from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from audit.models import AuditLog

from .admin_utils import base_ctx, staff_required


@staff_required
def admin_audit(request):
    action_filter = request.GET.get('action', 'all')
    model_filter = request.GET.get('model', 'all')
    user_filter = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    q = request.GET.get('q', '')

    qs = AuditLog.objects.all()
    if action_filter != 'all':
        qs = qs.filter(action=action_filter)
    if model_filter != 'all':
        qs = qs.filter(model_name__icontains=model_filter)
    if user_filter:
        qs = qs.filter(username__icontains=user_filter)
    if q:
        qs = qs.filter(description__icontains=q) | qs.filter(username__icontains=q)
    if date_from:
        qs = qs.filter(date_action__gte=date_from)
    if date_to:
        qs = qs.filter(date_action__lte=date_to)

    qs = qs.order_by('-date_action')[:100]

    stats = {
        'total': AuditLog.objects.count(),
        'actions': list(AuditLog.objects.values('action').annotate(count=Count('id')).order_by('-count')[:10]),
        'models': list(AuditLog.objects.values('model_name').annotate(count=Count('id')).order_by('-count')[:10]),
        'recent': AuditLog.objects.order_by('-date_action')[:5],
    }

    ctx = base_ctx(request, 'audit')
    ctx.update({
        'logs': qs,
        'stats': stats,
        'action_filter': action_filter,
        'model_filter': model_filter,
        'user_filter': user_filter,
        'date_from': date_from,
        'date_to': date_to,
        'q': q,
        'action_choices': AuditLog.ACTION_CHOICES,
    })
    return render(request, 'admin_cfld/audit.html', ctx)


@staff_required
def admin_audit_detail(request, pk):
    """Retourne les détails d'un log d'audit en JSON."""
    log = get_object_or_404(AuditLog, pk=pk)
    data = {
        'id': log.id,
        'action': log.action,
        'action_display': log.get_action_display(),
        'username': log.username,
        'user_id': log.user_id,
        'model_name': log.model_name,
        'object_id': log.object_id or '',
        'description': log.description,
        'ip_address': log.ip_address or '—',
        'localisation': log.localisation or '—',
        'user_agent': log.user_agent or '—',
        'url': log.url or '',
        'http_method': log.http_method or '',
        'date_action': log.date_action.strftime('%d/%m/%Y à %H:%M:%S'),
        'ancienne_valeur': log.ancienne_valeur,
        'nouvelle_valeur': log.nouvelle_valeur,
    }
    return JsonResponse(data)
