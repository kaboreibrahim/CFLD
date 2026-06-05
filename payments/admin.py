from django.contrib import admin
from .models import ComptePaiement, PaiementVisiteMedicale, PaiementInscription


@admin.register(ComptePaiement)
class ComptePaiementAdmin(admin.ModelAdmin):
    list_display = ['mode', 'numero', 'nom_titulaire', 'est_actif', 'ordre_affichage']
    list_filter = ['mode', 'est_actif']
    search_fields = ['numero', 'nom_titulaire']
    ordering = ['ordre_affichage', 'mode']


@admin.register(PaiementVisiteMedicale)
class PaiementVisiteMedicaleAdmin(admin.ModelAdmin):
    list_display = ['candidature', 'montant', 'compte_paiement', 'statut_validation', 'date_paiement']
    list_filter = ['statut_validation', 'date_paiement']
    search_fields = ['candidature__nom', 'candidature__prenom', 'candidature__reference']
    date_hierarchy = 'date_paiement'
    readonly_fields = ['date_creation', 'date_validation', 'valide_par']


@admin.register(PaiementInscription)
class PaiementInscriptionAdmin(admin.ModelAdmin):
    list_display = ['candidature', 'montant', 'compte_paiement', 'statut_validation', 'date_paiement']
    list_filter = ['statut_validation', 'date_paiement']
    search_fields = ['candidature__nom', 'candidature__prenom', 'candidature__reference']
    date_hierarchy = 'date_paiement'
    readonly_fields = ['date_creation', 'date_validation', 'valide_par']
