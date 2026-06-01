from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.generic import TemplateView, RedirectView
from django.views.static import serve
from django.contrib.sitemaps.views import sitemap

from core.sitemaps import AccueilSitemap, PagesSitemap, ArticlesSitemap, EquipesSitemap

sitemaps = {
    'accueil':  AccueilSitemap,
    'pages':    PagesSitemap,
    'articles': ArticlesSitemap,
    'equipes':  EquipesSitemap,
}

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # ── Pages principales ──────────────────────────────────────
    path('', include('pages.urls')),

    # ── Effectif + pages équipes ───────────────────────────────
    path('effectif/', include('effectif.urls')),

    # ── Matchs ────────────────────────────────────────────────
    path('matchs/', include('matchs.urls')),

    # ── Actualités (URLs SEO-friendly) ────────────────────────
    path('actualites/', include('medias.urls')),

    # ── Inscription (URL SEO-friendly) ────────────────────────
    path('inscription-joueur/', include('recrutement.urls')),

    # ── Contact ───────────────────────────────────────────────
    path('contact/', include('contact.urls')),

    # ── Admin custom ──────────────────────────────────────────
    path('admin-cfld/', include('recrutement.admin_urls')),

    # ── Médias / fichiers ─────────────────────────────────────
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # ── Redirects 301 depuis anciennes URLs ───────────────────
    path('inscription/', RedirectView.as_view(url='/inscription-joueur/', permanent=True)),
    path('medias/', RedirectView.as_view(url='/actualites/', permanent=True)),
    re_path(r'^medias/articles/(?P<pk>\d+)/$',
            RedirectView.as_view(pattern_name='article_detail', permanent=True)),

    # ── SEO ───────────────────────────────────────────────────
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

# Handlers d'erreur personnalisés
handler400 = 'core.views.erreur_400'
handler403 = 'core.views.erreur_403'
handler404 = 'core.views.erreur_404'
handler500 = 'core.views.erreur_500'

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from core import views as core_views

urlpatterns += staticfiles_urlpatterns()
urlpatterns += [
    path('erreurs/404/', core_views.erreur_404),
    path('erreurs/500/', core_views.erreur_500),
    path('erreurs/403/', core_views.erreur_403),
    path('erreurs/400/', core_views.erreur_400),
]
