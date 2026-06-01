from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.medias, name='medias'),
    # URL avec slug SEO-friendly
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    # Redirect 301 depuis l'ancienne URL avec pk
    path('articles/<int:pk>/', views.article_detail_by_pk, name='article_detail_pk'),
]
