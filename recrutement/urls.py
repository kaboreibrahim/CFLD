from django.urls import path
from . import views

urlpatterns = [
    path('', views.inscription, name='inscription'),
    # Téléchargement PDF par référence — accessible sans connexion
    path('pdf/<str:reference>/', views.telecharger_pdf_inscription, name='telecharger_pdf_inscription'),
]
