from django.contrib import admin
from .models import SEOPage


@admin.register(SEOPage)
class SEOPageAdmin(admin.ModelAdmin):
    list_display = ['page_id', 'titre_seo', 'indexation', 'modifie_le']
    search_fields = ['page_id', 'titre_seo', 'meta_description']
    list_filter = ['indexation']
    readonly_fields = ['modifie_le']
    fieldsets = [
        ('Identification', {
            'fields': ['page_id', 'slug_personnalise'],
        }),
        ('Balises Google', {
            'fields': ['titre_seo', 'meta_description', 'mots_cles'],
            'description': 'Ces champs apparaissent dans les résultats de recherche Google.',
        }),
        ('Partage social', {
            'fields': ['image_sociale'],
            'description': 'Image affichée lors du partage sur Facebook, WhatsApp, etc. (1200×630 px recommandé)',
        }),
        ('Indexation', {
            'fields': ['indexation'],
        }),
        ('Infos', {
            'fields': ['modifie_le'],
            'classes': ['collapse'],
        }),
    ]
