from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.generic import TemplateView
from django.views.static import serve
from django.contrib.sitemaps.views import sitemap

from core.sitemaps import AccueilSitemap, PagesSitemap, ArticlesSitemap

sitemaps = {
    'accueil':  AccueilSitemap,
    'pages':    PagesSitemap,
    'articles': ArticlesSitemap,
}

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('effectif/', include('effectif.urls')),
    path('matchs/', include('matchs.urls')),
    path('medias/', include('medias.urls')),
    path('inscription/', include('recrutement.urls')),
    path('contact/', include('contact.urls')),
    path('admin-cfld/', include('recrutement.admin_urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    # SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

# Handlers d'erreur personnalisés
handler400 = 'core.views.erreur_400'
handler403 = 'core.views.erreur_403'
handler404 = 'core.views.erreur_404'
handler500 = 'core.views.erreur_500'

# En développement : servir les fichiers statiques même avec DEBUG=False
# + URLs de prévisualisation des pages d'erreur
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from core import views as core_views

urlpatterns += staticfiles_urlpatterns()
urlpatterns += [
    path('erreurs/404/', core_views.erreur_404),
    path('erreurs/500/', core_views.erreur_500),
    path('erreurs/403/', core_views.erreur_403),
    path('erreurs/400/', core_views.erreur_400),
]
