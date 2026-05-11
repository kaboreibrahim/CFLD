from django.contrib import admin
from .models import Match, Classement


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'competition', 'journee', 'type_match', 'date']
    list_filter = ['type_match', 'competition', 'est_domicile']
    ordering = ['date']


@admin.register(Classement)
class ClassementAdmin(admin.ModelAdmin):
    list_display = ['equipe', 'points', 'matchs_joues', 'victoires', 'nuls', 'defaites', 'buts_pour', 'buts_contre', 'est_cfld']
    list_filter = ['saison', 'est_cfld']
    ordering = ['-points']
