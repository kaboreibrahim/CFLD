from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render

from recrutement.models import Candidature
from payments.models import ComptePaiement, PaiementInscription, PaiementVisiteMedicale


TYPE_CHOICES = [
    ('visite_medicale', 'Visite médicale'),
    ('inscription', "Frais d'inscription"),
]


def paiement_public(request):
    comptes_actifs = ComptePaiement.objects.filter(est_actif=True).order_by('ordre_affichage', 'mode')
    success = False

    if request.method == 'POST':
        type_frais = request.POST.get('type_frais', '').strip()
        reference = request.POST.get('reference_cfld', '').strip().upper()
        montant_raw = request.POST.get('montant', '').strip()
        compte_id = request.POST.get('compte_paiement', '').strip()
        reference_transaction = request.POST.get('reference_transaction', '').strip()
        capture = request.FILES.get('capture_depot')
        nom_soumetteur = request.POST.get('nom_soumetteur', '').strip()
        telephone_soumetteur = request.POST.get('telephone_soumetteur', '').strip()
        date_paiement = request.POST.get('date_paiement', '').strip() or None
        notes = request.POST.get('notes', '').strip()

        errors = {}

        if not type_frais or type_frais not in ('visite_medicale', 'inscription'):
            errors['type_frais'] = "Sélectionnez le type de frais."
        if not reference:
            errors['reference_cfld'] = "La référence CFLD est obligatoire."
        if not montant_raw:
            errors['montant'] = "Le montant est obligatoire."
        if not capture:
            errors['capture_depot'] = "La capture d'écran du dépôt est obligatoire."
        if not nom_soumetteur:
            errors['nom_soumetteur'] = "Votre nom est obligatoire."
        if not telephone_soumetteur:
            errors['telephone_soumetteur'] = "Votre numéro de téléphone est obligatoire."

        candidature = None
        if reference and not errors.get('reference_cfld'):
            try:
                candidature = Candidature.objects.get(reference=reference)
            except Candidature.DoesNotExist:
                errors['reference_cfld'] = f"Aucun dossier trouvé pour la référence « {reference} »."

        compte = None
        if compte_id:
            try:
                compte = ComptePaiement.objects.get(pk=compte_id, est_actif=True)
            except ComptePaiement.DoesNotExist:
                errors['compte_paiement'] = "Compte de paiement invalide."

        try:
            montant = int(montant_raw) if montant_raw else 0
            if montant <= 0:
                errors['montant'] = "Le montant doit être supérieur à 0."
        except ValueError:
            errors['montant'] = "Montant invalide."
            montant = 0

        if not errors and candidature:
            try:
                notes_full = f"Soumis par {nom_soumetteur} ({telephone_soumetteur})."
                if notes:
                    notes_full += f" {notes}"
                kwargs = dict(
                    candidature=candidature,
                    montant=montant,
                    compte_paiement=compte,
                    reference_transaction=reference_transaction,
                    capture_depot=capture,
                    statut_validation='pending',
                    notes=notes_full,
                )
                if date_paiement:
                    kwargs['date_paiement'] = date_paiement

                if type_frais == 'visite_medicale':
                    PaiementVisiteMedicale.objects.create(**kwargs)
                else:
                    PaiementInscription.objects.create(**kwargs)

                success = True
                messages.success(
                    request,
                    f"Votre demande de paiement ({dict(TYPE_CHOICES)[type_frais]}) a bien été soumise "
                    f"pour {candidature.nom_complet}. Elle sera vérifiée par l'administration."
                )
            except Exception:
                errors['global'] = "Une erreur est survenue. Veuillez réessayer."

        context = {
            'comptes_actifs': comptes_actifs,
            'errors': errors,
            'old': request.POST,
            'success': success,
            'type_choices': TYPE_CHOICES,
        }
        return render(request, 'payments/paiement_public.html', context)

    return render(request, 'payments/paiement_public.html', {
        'comptes_actifs': comptes_actifs,
        'type_choices': TYPE_CHOICES,
        'errors': {},
        'old': {},
        'success': False,
    })


def verifier_reference(request):
    """AJAX : vérifie une référence CFLD et retourne les infos candidature."""
    ref = request.GET.get('ref', '').strip().upper()
    if not ref:
        return JsonResponse({'found': False})
    try:
        c = Candidature.objects.get(reference=ref)
        return JsonResponse({
            'found': True,
            'nom_complet': c.nom_complet,
            'reference': c.reference,
            'categorie': c.categorie,
            'statut': c.get_statut_display(),
        })
    except Candidature.DoesNotExist:
        return JsonResponse({'found': False})
