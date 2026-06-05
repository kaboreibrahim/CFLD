from datetime import date as date_type
from functools import wraps

from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from django.db.models import Sum
from django.utils import timezone as tz

from effectif.models import Joueur
from recrutement.models import Candidature
from contact.models import Message

from .forms import (
    ComptePaiementForm, PaiementInscriptionForm, PaiementVisiteForm,
    CotisationAnnuelleForm, VersementForm,
)
from .models import (
    ComptePaiement, PaiementInscription, PaiementVisiteMedicale,
    CotisationAnnuelle, VersementCotisation,
    MONTANT_TOTAL_DEFAUT, MONTANT_PREMIER_VERSEMENT, MONTANT_MENSUEL,
)
from .services import calculer_echeances
from .pdf_utils import generer_recu_inscription, generer_recu_versement, generer_recu_visite_medicale


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def _base_ctx(request, section=''):
    return {
        'pending_count': Candidature.objects.filter(statut='pending').count(),
        'unread_count': Message.objects.filter(lu=False).count(),
        'section': section,
        'pending_visite': PaiementVisiteMedicale.objects.filter(statut_validation='pending').count(),
        'pending_inscription': PaiementInscription.objects.filter(statut_validation='pending').count(),
    }


# ── COMPTES DE PAIEMENT ───────────────────────────────────────

@staff_required
def admin_comptes_paiement(request):
    comptes = ComptePaiement.objects.all()
    ctx = _base_ctx(request, 'comptes_paiement')
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
    ctx = _base_ctx(request, 'comptes_paiement')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/compte_paiement_form.html', ctx)


@staff_required
def admin_compte_paiement_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(ComptePaiement, pk=pk).delete()
    return JsonResponse({'ok': True})


# ── PAIEMENTS VISITE MÉDICALE ─────────────────────────────────

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

    ctx = _base_ctx(request, 'paiements_visite')
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
    ctx = _base_ctx(request, 'paiements_visite')
    ctx.update({'form': form, 'obj': obj})
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


# ── PAIEMENTS INSCRIPTION ─────────────────────────────────────

@staff_required
def admin_paiements_inscription(request):
    q = request.GET.get('q', '')
    statut = request.GET.get('statut', 'all')
    qs = PaiementInscription.objects.select_related('candidature', 'compte_paiement', 'valide_par')

    if q:
        qs = qs.filter(
            Q(candidature__nom__icontains=q)
            | Q(candidature__prenom__icontains=q)
            | Q(candidature__reference__icontains=q)
        )
    if statut != 'all':
        qs = qs.filter(statut_validation=statut)

    ctx = _base_ctx(request, 'paiements_inscription')
    ctx.update({
        'paiements': qs,
        'total': PaiementInscription.objects.count(),
        'nb_pending': PaiementInscription.objects.filter(statut_validation='pending').count(),
        'nb_approved': PaiementInscription.objects.filter(statut_validation='approved').count(),
        'nb_rejected': PaiementInscription.objects.filter(statut_validation='rejected').count(),
        'q': q,
        'statut_actif': statut,
    })
    return render(request, 'admin_cfld/paiements_inscription.html', ctx)


@staff_required
def admin_paiement_inscription_form(request, pk=None):
    obj = get_object_or_404(PaiementInscription, pk=pk) if pk else None
    form = PaiementInscriptionForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        paiement = form.save(commit=False)
        paiement.enregistre_par = request.user
        paiement.save()
        messages.success(request, "Paiement inscription enregistré.")
        return redirect('admin_paiements_inscription')
    ctx = _base_ctx(request, 'paiements_inscription')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/paiement_inscription_form.html', ctx)


@staff_required
def admin_paiement_inscription_action(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    paiement = get_object_or_404(PaiementInscription, pk=pk)
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


# ── COTISATIONS ANNUELLES ─────────────────────────────────────

MOIS_LABELS = [
    (1,'Jan'), (2,'Fév'), (3,'Mar'), (4,'Avr'), (5,'Mai'), (6,'Jun'),
    (7,'Jul'), (8,'Aoû'), (9,'Sep'), (10,'Oct'), (11,'Nov'), (12,'Déc'),
]

@staff_required
def admin_cotisations_dashboard(request):
    annee = request.GET.get('annee', str(tz.localdate().year))
    try:
        annee = int(annee)
    except ValueError:
        annee = tz.localdate().year

    # -- Filtres mois / plage de date
    mois_str    = request.GET.get('mois', '').strip()
    date_debut_str = request.GET.get('date_debut', '').strip()
    date_fin_str   = request.GET.get('date_fin',   '').strip()

    mois = None
    if mois_str:
        try:
            m = int(mois_str)
            if 1 <= m <= 12:
                mois = m
        except ValueError:
            pass

    date_debut = date_fin = None
    if not mois:
        if date_debut_str:
            try:
                date_debut = date_type.fromisoformat(date_debut_str)
            except ValueError:
                date_debut_str = ''
        if date_fin_str:
            try:
                date_fin = date_type.fromisoformat(date_fin_str)
            except ValueError:
                date_fin_str = ''

    base_qs = (
        CotisationAnnuelle.objects
        .filter(annee=annee)
        .select_related('joueur')
        .prefetch_related('versements')
        .order_by('joueur__nom', 'joueur__prenom')
    )

    # Années disponibles pour le filtre
    annees = (
        CotisationAnnuelle.objects
        .values_list('annee', flat=True)
        .distinct()
        .order_by('-annee')
    )
    if not annees:
        annees = [tz.localdate().year]

    # KPIs toujours sur l'année complète
    all_cots = list(base_qs)
    total_joueurs  = len(all_cots)
    total_collecte = sum(c.total_verse   for c in all_cots)
    total_attendu  = sum(c.montant_total for c in all_cots)
    total_reste    = total_attendu - total_collecte
    nb_soldes      = sum(1 for c in all_cots if c.est_solde)
    nb_en_cours    = total_joueurs - nb_soldes

    # Tableau filtré
    cotisations = base_qs
    if mois:
        cotisations = cotisations.filter(
            versements__date_versement__month=mois
        ).distinct()
    else:
        if date_debut:
            cotisations = cotisations.filter(
                versements__date_versement__gte=date_debut
            ).distinct()
        if date_fin:
            cotisations = cotisations.filter(
                versements__date_versement__lte=date_fin
            ).distinct()

    # Joueurs sans cotisation cette année
    joueurs_sans_cotisation = Joueur.objects.filter(actif=True).exclude(
        cotisations_annuelles__annee=annee
    ).order_by('nom', 'prenom')

    ctx = _base_ctx(request, 'cotisations')
    ctx.update({
        'cotisations': cotisations,
        'annee': annee,
        'annees': annees,
        'mois': mois,
        'mois_choices': MOIS_LABELS,
        'date_debut': date_debut_str,
        'date_fin':   date_fin_str,
        'total_joueurs': total_joueurs,
        'total_collecte': total_collecte,
        'total_attendu': total_attendu,
        'total_reste': total_reste,
        'nb_soldes': nb_soldes,
        'nb_en_cours': nb_en_cours,
        'joueurs_sans_cotisation': joueurs_sans_cotisation,
        'montant_total_defaut': MONTANT_TOTAL_DEFAUT,
        'montant_premier': MONTANT_PREMIER_VERSEMENT,
        'montant_mensuel': MONTANT_MENSUEL,
    })
    return render(request, 'admin_cfld/cotisations_dashboard.html', ctx)


@staff_required
def admin_cotisation_creer(request):
    """Créer une cotisation annuelle pour un joueur (ou plusieurs via action groupée)."""
    if request.method == 'POST':
        form = CotisationAnnuelleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cotisation annuelle créée.")
            return redirect('admin_cotisations_dashboard')
    else:
        form = CotisationAnnuelleForm(initial={'annee': tz.localdate().year})
    ctx = _base_ctx(request, 'cotisations')
    ctx['form'] = form
    return render(request, 'admin_cfld/cotisation_form.html', ctx)


@staff_required
def admin_cotisation_creer_tous(request):
    """Crée une cotisation pour tous les joueurs actifs n'en ayant pas encore pour l'année."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    annee = int(request.POST.get('annee', tz.localdate().year))
    joueurs = Joueur.objects.filter(actif=True).exclude(
        cotisations_annuelles__annee=annee
    )
    nb = 0
    for j in joueurs:
        CotisationAnnuelle.objects.create(joueur=j, annee=annee)
        nb += 1
    return JsonResponse({'ok': True, 'nb': nb})


@staff_required
def admin_cotisation_detail(request, pk):
    cotisation = get_object_or_404(
        CotisationAnnuelle.objects.select_related('joueur').prefetch_related('versements'),
        pk=pk,
    )
    versements = cotisation.versements.select_related(
        'compte_paiement', 'valide_par', 'source_inscription'
    ).order_by('-date_versement')

    plan = calculer_echeances(cotisation)

    ctx = _base_ctx(request, 'cotisations')
    ctx.update({
        'cotisation': cotisation,
        'versements': versements,
        'plan': plan,
        'montant_echeance': MONTANT_MENSUEL,
    })
    return render(request, 'admin_cfld/cotisation_detail.html', ctx)


def _build_plan(cotisation):
    """Délègue au service services.calculer_echeances (10 échéances de 100k)."""
    return calculer_echeances(cotisation)


@staff_required
def admin_versement_add(request, cotisation_pk):
    cotisation = get_object_or_404(CotisationAnnuelle, pk=cotisation_pk)
    # Suggérer le montant selon l'avancement
    nb_valides = cotisation.nb_versements_valides
    if nb_valides == 0:
        montant_initial = int(MONTANT_PREMIER_VERSEMENT)
        type_initial = 'premier'
    else:
        montant_initial = int(MONTANT_MENSUEL)
        type_initial = 'mensuel'

    form = VersementForm(
        request.POST or None,
        request.FILES or None,
        initial={'montant': montant_initial, 'type_versement': type_initial},
    )
    if request.method == 'POST' and form.is_valid():
        v = form.save(commit=False)
        v.cotisation = cotisation
        v.enregistre_par = request.user
        v.save()
        messages.success(request, "Versement enregistré.")
        return redirect('admin_cotisation_detail', pk=cotisation_pk)

    ctx = _base_ctx(request, 'cotisations')
    ctx.update({'form': form, 'cotisation': cotisation})
    return render(request, 'admin_cfld/versement_form.html', ctx)


@staff_required
def admin_versement_action(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    v = get_object_or_404(VersementCotisation, pk=pk)
    action = request.POST.get('action')

    if action == 'approve':
        v.statut_validation = 'approved'
        v.valide_par = request.user
        v.save()
        return JsonResponse({'ok': True, 'statut': 'approved', 'total_verse': str(v.cotisation.total_verse), 'pct': v.cotisation.progression_pct})
    elif action == 'reject':
        v.statut_validation = 'rejected'
        v.valide_par = None
        v.save()
        return JsonResponse({'ok': True, 'statut': 'rejected'})
    elif action == 'delete':
        cot_pk = str(v.cotisation_id)
        v.delete()
        return JsonResponse({'ok': True, 'deleted': True, 'cotisation_pk': cot_pk})

    return JsonResponse({'error': 'Action inconnue'}, status=400)


# ── VUES PDF ─────────────────────────────────────────────────

@staff_required
def admin_inscription_detail(request, pk):
    paiement = get_object_or_404(
        PaiementInscription.objects.select_related(
            'candidature', 'compte_paiement', 'valide_par'
        ).prefetch_related('versement_cotisation'),
        pk=pk,
    )
    versement_auto = VersementCotisation.objects.filter(
        source_inscription=paiement
    ).select_related('cotisation', 'cotisation__joueur').first()

    plan = None
    if versement_auto:
        plan = calculer_echeances(versement_auto.cotisation)

    ctx = _base_ctx(request, "paiements_inscription")
    ctx.update({
        "paiement": paiement,
        "versement_auto": versement_auto,
        "plan": plan,
    })
    return render(request, "admin_cfld/inscription_detail.html", ctx)


@staff_required
def admin_inscription_pdf(request, pk):
    from django.http import HttpResponse
    paiement = get_object_or_404(PaiementInscription, pk=pk, statut_validation="approved")
    buf = generer_recu_inscription(paiement)
    numero = paiement.candidature.reference
    response = HttpResponse(buf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=recu_inscription_{numero}.pdf'
    return response


@staff_required
def admin_versement_pdf(request, pk):
    from django.http import HttpResponse
    versement = get_object_or_404(VersementCotisation, pk=pk, statut_validation="approved")
    buf = generer_recu_versement(versement)
    joueur = versement.cotisation.joueur.nom.replace(" ", "_")
    response = HttpResponse(buf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=recu_versement_{joueur}_{versement.cotisation.annee}.pdf'
    return response


@staff_required
def admin_visite_pdf(request, pk):
    from django.http import HttpResponse
    paiement = get_object_or_404(PaiementVisiteMedicale, pk=pk, statut_validation='approved')
    buf = generer_recu_visite_medicale(paiement)
    ref = paiement.candidature.reference
    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_visite_{ref}.pdf"'
    return response
