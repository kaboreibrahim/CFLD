from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from audit.utils import log_download
from payments.models import PaiementVisiteMedicale, VersementCotisation
from payments.pdf_utils import generer_recu_versement, generer_recu_visite_medicale

from .admin_utils import staff_required


@staff_required
def admin_versement_pdf(request, pk):
    versement = get_object_or_404(VersementCotisation, pk=pk, statut_validation="approved")
    log_download(request, "VersementCotisation",
                 f"Telechargement du recu versement {versement}.", versement.pk)
    buf = generer_recu_versement(versement)
    joueur = versement.cotisation.joueur.nom.replace(" ", "_")
    response = HttpResponse(buf, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename=recu_versement_{joueur}_{versement.cotisation.annee}.pdf'
    )
    return response


@staff_required
def admin_visite_pdf(request, pk):
    paiement = get_object_or_404(PaiementVisiteMedicale, pk=pk, statut_validation='approved')
    log_download(request, "PaiementVisiteMedicale",
                 f"Telechargement du recu visite medicale {paiement}.", paiement.pk)
    buf = generer_recu_visite_medicale(paiement)
    ref = paiement.candidature.reference
    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_visite_{ref}.pdf"'
    return response
