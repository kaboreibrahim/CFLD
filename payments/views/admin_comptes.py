from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from audit.utils import log_view
from payments.forms import ComptePaiementForm
from payments.models import ComptePaiement

from .admin_utils import base_ctx, staff_required


@staff_required
def admin_comptes_paiement(request):
    comptes = ComptePaiement.objects.all()
    log_view(request, "ComptePaiement", "Consultation de la liste des comptes de paiement.")
    ctx = base_ctx(request, 'comptes_paiement')
    ctx['comptes'] = comptes
    ctx['total'] = comptes.count()
    return render(request, 'admin_cfld/comptes_paiement.html', ctx)


@staff_required
def admin_compte_paiement_form(request, pk=None):
    obj = get_object_or_404(ComptePaiement, pk=pk) if pk else None
    form = ComptePaiementForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Compte de paiement enregistré avec succès.")
        return redirect('admin_comptes_paiement')
    ctx = base_ctx(request, 'comptes_paiement')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/compte_paiement_form.html', ctx)


@staff_required
def admin_compte_paiement_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(ComptePaiement, pk=pk).delete()
    return JsonResponse({'ok': True})
