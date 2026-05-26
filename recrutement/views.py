from django.shortcuts import render
from django.http import JsonResponse
from .forms import CandidatureForm
from .whatsapp import notifier_admin, confirmer_candidat


def inscription(request):
    if request.method == 'POST':
        form = CandidatureForm(request.POST, request.FILES)
        if form.is_valid():
            candidature = form.save()
            notifier_admin(candidature)
            confirmer_candidat(candidature)
            return JsonResponse({
                'success': True,
                'reference': candidature.reference,
            })
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = CandidatureForm()
    return render(request, 'recrutement/inscription.html', {'form': form})
