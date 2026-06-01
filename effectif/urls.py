from django.urls import path
from . import views

urlpatterns = [
    path('', views.effectif, name='effectif'),
    # Pages équipes dédiées — URL SEO-friendly
    path('equipes/<slug:equipe_slug>/', views.equipe_detail, name='equipe_detail'),
]
