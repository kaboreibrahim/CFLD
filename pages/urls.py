from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('club/', views.club, name='club'),
    # URL SEO-friendly
    path('centre-formation-football/', views.academie, name='academie'),
    # Redirect 301 depuis l'ancienne URL
    path('academie/', RedirectView.as_view(url='/centre-formation-football/', permanent=True)),
]
