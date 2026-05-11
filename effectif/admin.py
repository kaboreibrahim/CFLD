from django.contrib import admin
from .models import Joueur


@admin.register(Joueur)
class JoueurAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nom_complet', 'poste', 'age', 'matchs_joues', 'buts', 'actif']
    list_filter = ['poste', 'actif', 'nationalite']
    search_fields = ['nom', 'prenom']
    list_editable = ['actif']
    ordering = ['poste', 'numero']
