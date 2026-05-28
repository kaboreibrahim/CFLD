from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from medias.models import Article


class AccueilSitemap(Sitemap):
    """Page d'accueil — priorité maximale."""
    protocol = 'https'
    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        return ['accueil']

    def location(self, item):
        return reverse(item)


class PagesSitemap(Sitemap):
    """Pages statiques principales du site."""
    protocol = 'https'
    changefreq = 'monthly'

    # (url_name, priority)
    _pages = [
        ('club',        0.8),
        ('academie',    0.8),
        ('inscription', 0.8),
        ('effectif',    0.7),
        ('matchs',      0.7),
        ('medias',      0.7),
        ('contact',     0.6),
    ]

    def items(self):
        return self._pages

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]


class ArticlesSitemap(Sitemap):
    """Articles publiés — mis à jour selon date de publication."""
    protocol = 'https'
    changefreq = 'monthly'
    priority = 0.65

    def items(self):
        return Article.objects.filter(publie=True).order_by('-date_publication')

    def lastmod(self, obj):
        return obj.date_publication

    def location(self, obj):
        return reverse('article_detail', args=[obj.pk])
