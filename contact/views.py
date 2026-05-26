from django.shortcuts import render
from django.http import JsonResponse
from .forms import MessageForm
from .whatsapp import envoyer_notification_whatsapp


def contact(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save()
            envoyer_notification_whatsapp(message)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = MessageForm()
    return render(request, 'contact/contact.html', {'form': form})
