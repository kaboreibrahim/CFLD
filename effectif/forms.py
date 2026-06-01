from django import forms
from .models import Joueur


class JoueurForm(forms.ModelForm):
    class Meta:
        model = Joueur
        fields = [
            'prenom', 'nom', 'numero', 'poste', 'sexe', 'categorie',
            'age', 'matchs_joues', 'buts', 'nationalite',
            'numero_licence', 'date_inscription',
            'photo', 'actif',
        ]
        widgets = {
            'prenom':          forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'nom':             forms.TextInput(attrs={'placeholder': 'Nom'}),
            'numero':          forms.NumberInput(attrs={'min': 1, 'max': 99}),
            'age':             forms.NumberInput(attrs={'min': 8, 'max': 45}),
            'matchs_joues':    forms.NumberInput(attrs={'min': 0}),
            'buts':            forms.NumberInput(attrs={'min': 0}),
            'nationalite':     forms.TextInput(attrs={'placeholder': "Côte d'Ivoire"}),
            'numero_licence':  forms.TextInput(attrs={'placeholder': 'Ex. FIF-2026-0001'}),
            'date_inscription': forms.DateInput(attrs={'type': 'date'}),
        }
