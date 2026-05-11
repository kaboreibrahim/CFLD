from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('club/', views.club, name='club'),
    path('academie/', views.academie, name='academie'),
]
