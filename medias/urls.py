from django.urls import path
from . import views

urlpatterns = [
    path('', views.medias, name='medias'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),
]
