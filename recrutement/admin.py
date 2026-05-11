from django.contrib import admin
from .models import Candidature


@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = ['reference', 'nom_complet', 'poste', 'age', 'statut', 'date_soumission', 'notifie']
    list_filter = ['statut', 'poste', 'nationalite']
    search_fields = ['nom', 'prenom', 'email', 'reference']
    list_editable = ['statut']
    readonly_fields = ['reference', 'date_soumission']
    ordering = ['-date_soumission']

    actions = ['accepter', 'refuser', 'mettre_en_attente']

    @admin.action(description='Accepter les candidatures sélectionnées')
    def accepter(self, request, queryset):
        queryset.update(statut='accepted')

    @admin.action(description='Refuser les candidatures sélectionnées')
    def refuser(self, request, queryset):
        queryset.update(statut='refused')

    @admin.action(description='Mettre en attente les candidatures sélectionnées')
    def mettre_en_attente(self, request, queryset):
        queryset.update(statut='waiting')
