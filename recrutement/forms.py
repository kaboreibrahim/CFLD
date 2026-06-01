from django import forms
from .models import Candidature


class CandidatureForm(forms.ModelForm):
    consentement = forms.BooleanField(required=True)

    class Meta:
        model = Candidature
        fields = [
            'nom', 'prenom', 'date_naissance', 'sexe', 'categorie',
            'nationalite', 'poste', 'numero_prefere', 'pied_fort', 'ancien_club',
            'telephone_whatsapp', 'email', 'adresse',
            'nom_parent', 'telephone_parent', 'email_parent',
            'info_scolaire', 'contact_urgence',
            'photo',
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'numero_prefere': forms.NumberInput(attrs={'min': 1, 'max': 99}),
        }
