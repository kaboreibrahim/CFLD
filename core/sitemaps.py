from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from medias.models import Article


class AccueilSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        return ['accueil']

    def location(self, item):
        return reverse(item)


class PagesSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'monthly'

    _pages = [
        ('club',        0.8),
        ('academie',    0.85),
        ('inscription', 0.9),   # priorité haute — acquisition joueurs
        ('effectif',    0.75),
        ('matchs',      0.7),
        ('medias',      0.8),
        ('contact',     0.6),
    ]

    def items(self):
        return self._pages

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]


class ArticlesSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Article.objects.filter(publie=True).order_by('-date_publication')

    def lastmod(self, obj):
        return obj.date_publication

    def location(self, obj):
        return reverse('article_detail', args=[obj.slug])


class EquipesSitemap(Sitemap):
    """Pages dédiées aux 6 équipes — fort potentiel SEO."""
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.85

    _equipes = [
        'u10-masculin',
        'u13-masculin',
        'u15-masculin',
        'u17-masculin',
        'u12-feminin',
        'u15-feminin',
    ]

    def items(self):
        return self._equipes

    def location(self, slug):
        return reverse('equipe_detail', args=[slug])
