from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from pages.forms import InfoTickerForm
from pages.models import InfoTicker

from .admin_utils import base_ctx, staff_required


@staff_required
def admin_ticker(request):
    qs = InfoTicker.objects.all()
    ctx = base_ctx(request, 'ticker')
    ctx.update({'items': qs})
    return render(request, 'admin_cfld/ticker.html', ctx)


@staff_required
def admin_ticker_form(request, pk=None):
    obj = get_object_or_404(InfoTicker, pk=pk) if pk else None
    form = InfoTickerForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_ticker')
    ctx = base_ctx(request, 'ticker')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/ticker_form.html', ctx)


@staff_required
def admin_ticker_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(InfoTicker, pk=pk).delete()
    return JsonResponse({'ok': True})
