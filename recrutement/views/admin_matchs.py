from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from matchs.forms import ClassementForm, MatchForm
from matchs.models import Classement, Match

from .admin_utils import base_ctx, staff_required


# ── MATCHS ───────────────────────────────────────────────────

@staff_required
def admin_matchs(request):
    type_m = request.GET.get('type', 'all')
    qs = Match.objects.all()
    if type_m != 'all':
        qs = qs.filter(type_match=type_m)
    ctx = base_ctx(request, 'matchs')
    ctx.update({'matchs': qs, 'type_actif': type_m, 'total': Match.objects.count()})
    return render(request, 'admin_cfld/matchs.html', ctx)


@staff_required
def admin_match_form(request, pk=None):
    obj = get_object_or_404(Match, pk=pk) if pk else None
    form = MatchForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_matchs')
    ctx = base_ctx(request, 'matchs')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/match_form.html', ctx)


@staff_required
def admin_match_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(Match, pk=pk).delete()
    return JsonResponse({'ok': True})


# ── CLASSEMENT ───────────────────────────────────────────────

@staff_required
def admin_classement(request):
    saison = request.GET.get('saison', '')
    qs = Classement.objects.all()
    if saison:
        qs = qs.filter(saison=saison)
    saisons = Classement.objects.values_list('saison', flat=True).distinct()
    ctx = base_ctx(request, 'classement')
    ctx.update({'classement': qs, 'saison': saison, 'saisons': saisons})
    return render(request, 'admin_cfld/classement.html', ctx)


@staff_required
def admin_classement_form(request, pk=None):
    obj = get_object_or_404(Classement, pk=pk) if pk else None
    form = ClassementForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_classement')
    ctx = base_ctx(request, 'classement')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/classement_form.html', ctx)


@staff_required
def admin_classement_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(Classement, pk=pk).delete()
    return JsonResponse({'ok': True})
