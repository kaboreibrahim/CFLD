from django.contrib import admin
from .models import InfoTicker


@admin.register(InfoTicker)
class InfoTickerAdmin(admin.ModelAdmin):
    list_display  = ('__str__', 'type', 'categorie', 'actif', 'ordre')
    list_editable = ('actif', 'ordre')
    list_filter   = ('type', 'actif')
    ordering      = ('ordre', 'pk')
    fieldsets = (
        ('Type & ordre', {'fields': ('type', 'ordre', 'actif')}),
        ('Score / Match', {
            'fields': ('categorie', 'equipe_dom', 'equipe_ext',
                       'score_dom', 'score_ext', 'minute'),
            'description': 'Remplir pour les types « Score en direct » et « Résultat ».',
        }),
        ('Texte libre', {
            'fields': ('texte',),
            'description': 'Remplir pour les types « Annonce » et « Prochain match ».',
        }),
    )
