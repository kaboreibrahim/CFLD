from django.urls import path
from . import views

urlpatterns = [
    path('', views.paiement_public, name='paiement_public'),
    path('verifier-reference/', views.verifier_reference, name='paiement_verifier_reference'),
]
