from django.urls import path
from . import views

urlpatterns = [
    path('', views.medias, name='medias'),
]
