from django import forms
from .models import Match, Classement


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['equipe_domicile', 'equipe_exterieur', 'est_domicile',
                  'score_domicile', 'score_exterieur', 'date', 'lieu',
                  'competition', 'journee', 'type_match', 'billet_url']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'billet_url': forms.URLInput(attrs={'placeholder': 'https://…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.date:
            self.fields['date'].initial = self.instance.date.strftime('%Y-%m-%dT%H:%M')


class ClassementForm(forms.ModelForm):
    class Meta:
        model = Classement
        fields = ['equipe', 'points', 'matchs_joues', 'victoires',
                  'nuls', 'defaites', 'buts_pour', 'buts_contre',
                  'est_cfld', 'saison']
        widgets = {
            'saison': forms.TextInput(attrs={'placeholder': '2025-2026'}),
        }
