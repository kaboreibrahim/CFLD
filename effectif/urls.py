from django.urls import path
from . import views

urlpatterns = [
    path('', views.effectif, name='effectif'),
]
