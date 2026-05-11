from django.shortcuts import render
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
