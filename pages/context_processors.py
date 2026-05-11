from .models import InfoTicker


def ticker(request):
    return {
        'ticker_items': InfoTicker.objects.filter(actif=True).order_by('ordre', 'pk')
    }
