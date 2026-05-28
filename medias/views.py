from django.shortcuts import render, get_object_or_404
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


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, publie=True)
    autres = Article.objects.filter(publie=True).exclude(pk=pk).order_by('-date_publication')[:3]
    return render(request, 'medias/article_detail.html', {
        'article': article,
        'autres': autres,
    })
