from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from audit.utils import log_view
from payments.forms import PaiementVisiteForm
from payments.models import PaiementVisiteMedicale

from .admin_utils import base_ctx, comptes_json, staff_required


@staff_required
def admin_paiements_visite(request):
    q = request.GET.get('q', '')
    statut = request.GET.get('statut', 'all')
    qs = PaiementVisiteMedicale.objects.select_related('candidature', 'compte_paiement', 'valide_par')

    if q:
        qs = qs.filter(
            Q(candidature__nom__icontains=q)
            | Q(candidature__prenom__icontains=q)
            | Q(candidature__reference__icontains=q)
        )
    if statut != 'all':
        qs = qs.filter(statut_validation=statut)

    log_view(request, "PaiementVisiteMedicale", "Consultation de la liste des paiements visite medicale.")
    ctx = base_ctx(request, 'paiements_visite')
    ctx.update({
        'paiements': qs,
        'total': PaiementVisiteMedicale.objects.count(),
        'nb_pending': PaiementVisiteMedicale.objects.filter(statut_validation='pending').count(),
        'nb_approved': PaiementVisiteMedicale.objects.filter(statut_validation='approved').count(),
        'nb_rejected': PaiementVisiteMedicale.objects.filter(statut_validation='rejected').count(),
        'q': q,
        'statut_actif': statut,
    })
    return render(request, 'admin_cfld/paiements_visite.html', ctx)


@staff_required
def admin_paiement_visite_form(request, pk=None):
    obj = get_object_or_404(PaiementVisiteMedicale, pk=pk) if pk else None
    form = PaiementVisiteForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        paiement = form.save(commit=False)
        paiement.enregistre_par = request.user
        paiement.save()
        messages.success(request, "Paiement visite médicale enregistré.")
        return redirect('admin_paiements_visite')
    ctx = base_ctx(request, 'paiements_visite')
    ctx.update({'form': form, 'obj': obj, 'comptes_json': comptes_json()})
    return render(request, 'admin_cfld/paiement_visite_form.html', ctx)


@staff_required
def admin_paiement_visite_action(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    paiement = get_object_or_404(PaiementVisiteMedicale, pk=pk)
    action = request.POST.get('action')

    if action == 'approve':
        paiement.statut_validation = 'approved'
        paiement.valide_par = request.user
        paiement.date_validation = timezone.now()
        paiement.save()
        return JsonResponse({'ok': True, 'statut': 'approved'})
    elif action == 'reject':
        paiement.statut_validation = 'rejected'
        paiement.valide_par = None
        paiement.date_validation = None
        paiement.save()
        return JsonResponse({'ok': True, 'statut': 'rejected'})
    elif action == 'delete':
        paiement.delete()
        return JsonResponse({'ok': True, 'deleted': True})

    return JsonResponse({'error': 'Action inconnue'}, status=400)
