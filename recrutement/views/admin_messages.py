from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from contact.models import Message

from .admin_utils import base_ctx, staff_required


@staff_required
def admin_messages(request):
    filtre = request.GET.get('filtre', 'all')
    qs = Message.objects.all()
    if filtre == 'non_lu':
        qs = qs.filter(lu=False)
    ctx = base_ctx(request, 'messages')
    ctx.update({'messages_list': qs, 'filtre': filtre, 'total': Message.objects.count()})
    return render(request, 'admin_cfld/messages.html', ctx)


@staff_required
def admin_message_detail(request, pk):
    msg = get_object_or_404(Message, pk=pk)
    if not msg.lu:
        msg.lu = True
        msg.save()
    ctx = base_ctx(request, 'messages')
    ctx.update({'msg': msg})
    return render(request, 'admin_cfld/message_detail.html', ctx)


@staff_required
def admin_message_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(Message, pk=pk).delete()
    return JsonResponse({'ok': True})
