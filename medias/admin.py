from django.contrib import admin
from .models import Article, Photo, Video


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['titre', 'categorie', 'date_publication', 'en_une', 'publie']
    list_filter = ['categorie', 'en_une', 'publie']
    search_fields = ['titre', 'contenu']
    list_editable = ['publie', 'en_une']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['legende', 'date', 'afficher']
    list_editable = ['afficher']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type_video', 'date', 'afficher']
    list_editable = ['afficher']
