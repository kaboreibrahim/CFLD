from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from medias.forms import ArticleForm, PhotoForm, VideoForm
from medias.models import Article, Photo, Video

from .admin_utils import base_ctx, staff_required


# ── ARTICLES ─────────────────────────────────────────────────

@staff_required
def admin_articles(request):
    q = request.GET.get('q', '')
    cat = request.GET.get('cat', 'all')
    qs = Article.objects.all()
    if q:
        qs = qs.filter(titre__icontains=q)
    if cat != 'all':
        qs = qs.filter(categorie=cat)
    ctx = base_ctx(request, 'articles')
    ctx.update({'articles': qs, 'q': q, 'cat_actif': cat, 'total': Article.objects.count()})
    return render(request, 'admin_cfld/articles.html', ctx)


@staff_required
def admin_article_form(request, pk=None):
    obj = get_object_or_404(Article, pk=pk) if pk else None
    form = ArticleForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_articles')
    ctx = base_ctx(request, 'articles')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/article_form.html', ctx)


@staff_required
def admin_article_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(Article, pk=pk).delete()
    return JsonResponse({'ok': True})


# ── PHOTOS ───────────────────────────────────────────────────

@staff_required
def admin_photos(request):
    qs = Photo.objects.all()
    ctx = base_ctx(request, 'photos')
    ctx.update({'photos': qs})
    return render(request, 'admin_cfld/photos.html', ctx)


@staff_required
def admin_photo_form(request, pk=None):
    obj = get_object_or_404(Photo, pk=pk) if pk else None
    form = PhotoForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_photos')
    ctx = base_ctx(request, 'photos')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/photo_form.html', ctx)


@staff_required
def admin_photo_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(Photo, pk=pk).delete()
    return JsonResponse({'ok': True})


# ── VIDÉOS ───────────────────────────────────────────────────

@staff_required
def admin_videos(request):
    qs = Video.objects.all()
    ctx = base_ctx(request, 'videos')
    ctx.update({'videos': qs})
    return render(request, 'admin_cfld/videos.html', ctx)


@staff_required
def admin_video_form(request, pk=None):
    obj = get_object_or_404(Video, pk=pk) if pk else None
    form = VideoForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_videos')
    ctx = base_ctx(request, 'videos')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/video_form.html', ctx)


@staff_required
def admin_video_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(Video, pk=pk).delete()
    return JsonResponse({'ok': True})
