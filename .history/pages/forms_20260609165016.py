from django import forms
from .models import InfoTicker


class InfoTickerForm(forms.ModelForm):
    class Meta:
        model = InfoTicker
        fields = ['type', 'categorie', 'equipe_dom', 'equipe_ext',
                  'score_dom', 'score_ext', 'minute', 'texte', 'actif', 'ordre']
        widgets = {
            'categorie':  forms.TextInput(attrs={'placeholder': 'Ex : U17, Ligue 1 CI'}),
            'equipe_dom': forms.TextInput(attrs={'placeholder': 'Équipe domicile'}),
            'equipe_ext': forms.TextInput(attrs={'placeholder': 'Équipe extérieur'}),
            'texte':      forms.TextInput(attrs={'placeholder': 'Texte libre (annonce / prochain match)'}),
        }

