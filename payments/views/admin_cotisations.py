from datetime import date as date_type

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone as tz

from audit.utils import log_view
from effectif.models import Joueur
from payments.forms import CotisationAnnuelleForm, VersementForm
from payments.models import (
    CotisationAnnuelle,
    MONTANT_MENSUEL,
    MONTANT_PREMIER_VERSEMENT,
    MONTANT_TOTAL_DEFAUT,
    VersementCotisation,
)
from payments.services import calculer_echeances

from .admin_utils import base_ctx, comptes_json, staff_required


MOIS_LABELS = [
    (1, 'Jan'), (2, 'Fév'), (3, 'Mar'), (4, 'Avr'), (5, 'Mai'), (6, 'Jun'),
    (7, 'Jul'), (8, 'Aoû'), (9, 'Sep'), (10, 'Oct'), (11, 'Nov'), (12, 'Déc'),
]


@staff_required
def admin_cotisations_dashboard(request):
    annee = request.GET.get('annee', str(tz.localdate().year))
    try:
        annee = int(annee)
    except ValueError:
        annee = tz.localdate().year

    mois_str = request.GET.get('mois', '').strip()
    date_debut_str = request.GET.get('date_debut', '').strip()
    date_fin_str = request.GET.get('date_fin', '').strip()

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

    annees = (
        CotisationAnnuelle.objects
        .values_list('annee', flat=True)
        .distinct()
        .order_by('-annee')
    )
    if not annees:
        annees = [tz.localdate().year]

    all_cots = list(base_qs)
    total_joueurs = len(all_cots)
    total_collecte = sum(c.total_verse for c in all_cots)
    total_attendu = sum(c.montant_total for c in all_cots)
    total_reste = total_attendu - total_collecte
    nb_soldes = sum(1 for c in all_cots if c.est_solde)
    nb_en_cours = total_joueurs - nb_soldes

    cotisations = base_qs
    if mois:
        cotisations = cotisations.filter(versements__date_versement__month=mois).distinct()
    else:
        if date_debut:
            cotisations = cotisations.filter(
                versements__date_versement__gte=date_debut
            ).distinct()
        if date_fin:
            cotisations = cotisations.filter(
                versements__date_versement__lte=date_fin
            ).distinct()

    joueurs_sans_cotisation = Joueur.objects.filter(actif=True).exclude(
        cotisations_annuelles__annee=annee
    ).order_by('nom', 'prenom')

    log_view(request, "CotisationAnnuelle", f"Consultation du tableau de bord cotisations {annee}.")
    ctx = base_ctx(request, 'cotisations')
    ctx.update({
        'cotisations': cotisations,
        'annee': annee,
        'annees': annees,
        'mois': mois,
        'mois_choices': MOIS_LABELS,
        'date_debut': date_debut_str,
        'date_fin': date_fin_str,
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
    if request.method == 'POST':
        form = CotisationAnnuelleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cotisation annuelle créée.")
            return redirect('admin_cotisations_dashboard')
    else:
        form = CotisationAnnuelleForm(initial={'annee': tz.localdate().year})
    ctx = base_ctx(request, 'cotisations')
    ctx['form'] = form
    return render(request, 'admin_cfld/cotisation_form.html', ctx)


@staff_required
def admin_cotisation_creer_tous(request):
    """Crée une cotisation pour tous les joueurs actifs n'en ayant pas encore pour l'année."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    annee = int(request.POST.get('annee', tz.localdate().year))
    joueurs = Joueur.objects.filter(actif=True).exclude(cotisations_annuelles__annee=annee)
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

    log_view(request, "CotisationAnnuelle",
             f"Consultation du detail de la cotisation {cotisation}.", cotisation.pk)
    ctx = base_ctx(request, 'cotisations')
    ctx.update({
        'cotisation': cotisation,
        'versements': versements,
        'plan': plan,
        'montant_echeance': MONTANT_MENSUEL,
    })
    return render(request, 'admin_cfld/cotisation_detail.html', ctx)


@staff_required
def admin_versement_add(request, cotisation_pk):
    cotisation = get_object_or_404(CotisationAnnuelle, pk=cotisation_pk)
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

    ctx = base_ctx(request, 'cotisations')
    ctx.update({'form': form, 'cotisation': cotisation, 'comptes_json': comptes_json()})
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
        return JsonResponse({
            'ok': True, 'statut': 'approved',
            'total_verse': str(v.cotisation.total_verse),
            'pct': v.cotisation.progression_pct,
        })
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
