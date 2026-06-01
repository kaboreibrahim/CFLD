from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Photo, Video


def medias(request):
    article_une = Article.objects.filter(publie=True, en_une=True).first()
    articles = Article.objects.filter(publie=True).order_by('-date_publication')[:6]
    photos = Photo.objects.filter(afficher=True)
    videos = Video.objects.filter(afficher=True)

    return render(request, 'medias/medias.html', {
        'article_une': article_une,
        'articles': articles,
        'photos': photos,
        'videos': videos,
    })


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, publie=True)
    autres = Article.objects.filter(publie=True).exclude(slug=slug).order_by('-date_publication')[:3]
    return render(request, 'medias/article_detail.html', {
        'article': article,
        'autres': autres,
    })


def article_detail_by_pk(request, pk):
    """Redirect 301 depuis l'ancienne URL /actualites/articles/<pk>/."""
    article = get_object_or_404(Article, pk=pk, publie=True)
    if not article.slug:
        article.save()  # génère le slug
    return redirect('article_detail', slug=article.slug, permanent=True)
