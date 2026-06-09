"""
Utilitaires partagés par les vues admin du module payments.
"""
import json
from functools import wraps

from django.shortcuts import redirect

from contact.models import Message
from payments.models import (
    ComptePaiement,
    PaiementInscription,
    PaiementVisiteMedicale,
)
from recrutement.models import Candidature


def staff_required(view_func):
    """Redirige vers /login si l'utilisateur n'est pas staff."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def base_ctx(request, section=''):
    """Contexte commun pour tous les templates admin paiements."""
    return {
        'pending_count': Candidature.objects.filter(statut='pending').count(),
        'unread_count': Message.objects.filter(lu=False).count(),
        'section': section,
        'pending_visite': PaiementVisiteMedicale.objects.filter(statut_validation='pending').count(),
        'pending_inscription': PaiementInscription.objects.filter(statut_validation='pending').count(),
    }


def comptes_json():
    """Retourne les comptes actifs sérialisés en JSON pour les formulaires JS."""
    return json.dumps(
        {str(c.pk): {'lien': c.lien, 'numero': c.numero, 'mode': c.get_mode_display()}
         for c in ComptePaiement.objects.filter(est_actif=True)},
        ensure_ascii=False,
    )
