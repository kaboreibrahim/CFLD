import os

from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render

from recrutement.forms import CandidatureForm
from recrutement.models import Candidature
from recrutement.pdf_utils import generer_pdf_inscription
from recrutement.whatsapp import confirmer_candidat, notifier_admin


def inscription(request):
    if request.method == 'POST':
        form = CandidatureForm(request.POST, request.FILES)
        if form.is_valid():
            candidature = form.save()

            pdf_url = None
            try:
                generer_pdf_inscription(candidature)
                candidature.refresh_from_db()
                if candidature.pdf_inscription:
                    pdf_url = f'/inscription-joueur/pdf/{candidature.reference}/'
            except Exception:
                pass

            try:
                notifier_admin(candidature)
                confirmer_candidat(candidature)
            except Exception:
                pass

            return JsonResponse({
                'success': True,
                'reference': candidature.reference,
                'pdf_url': pdf_url,
            })

        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = CandidatureForm()
    return render(request, 'recrutement/inscription.html', {'form': form})


def telecharger_pdf_inscription(request, reference):
    """
    Vue publique — le candidat télécharge son propre PDF via sa référence.
    Aucune authentification requise : la référence unique suffit.
    """
    candidature = get_object_or_404(Candidature, reference=reference)

    if not candidature.pdf_inscription:
        try:
            generer_pdf_inscription(candidature)
            candidature.refresh_from_db()
        except Exception:
            raise Http404('PDF non disponible')

    pdf_path = os.path.join(settings.MEDIA_ROOT, str(candidature.pdf_inscription))
    if not os.path.exists(pdf_path):
        raise Http404('Fichier PDF introuvable')

    return FileResponse(
        open(pdf_path, 'rb'),
        as_attachment=True,
        filename=f'inscription_{candidature.reference}.pdf',
        content_type='application/pdf',
    )
