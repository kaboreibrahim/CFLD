from django import forms
from .models import Joueur


class JoueurForm(forms.ModelForm):
    class Meta:
        model = Joueur
        fields = [
            # Identité
            'prenom', 'nom', 'date_naissance', 'sexe', 'categorie',
            'nationalite', 'adresse',
            # Profil sportif
            'numero', 'poste', 'pied_fort', 'ancien_club',
            # Contact joueur
            'telephone_whatsapp', 'email',
            # Parent / tuteur
            'nom_parent', 'telephone_parent', 'email_parent',
            # Infos complémentaires
            'info_scolaire', 'contact_urgence',
            # Photo & stats
            'photo', 'matchs_joues', 'buts',
            # Admin
            'numero_licence', 'date_inscription', 'actif',
        ]
        widgets = {
            'prenom':             forms.TextInput(attrs={'placeholder': 'Prénom du joueur'}),
            'nom':                forms.TextInput(attrs={'placeholder': 'Nom de famille'}),
            'date_naissance':     forms.DateInput(attrs={'type': 'date'}),
            'adresse':            forms.TextInput(attrs={'placeholder': 'Adresse complète'}),
            'numero':             forms.NumberInput(attrs={'min': 1, 'max': 99, 'placeholder': '10'}),
            'ancien_club':        forms.TextInput(attrs={'placeholder': 'Nom du club précédent (optionnel)'}),
            'telephone_whatsapp': forms.TextInput(attrs={'placeholder': '+225 07 00 00 00 00'}),
            'email':              forms.EmailInput(attrs={'placeholder': 'joueur@email.com'}),
            'nom_parent':         forms.TextInput(attrs={'placeholder': 'Nom et prénom du parent/tuteur'}),
            'telephone_parent':   forms.TextInput(attrs={'placeholder': '+225 07 00 00 00 00'}),
            'email_parent':       forms.EmailInput(attrs={'placeholder': 'parent@email.com'}),
            'info_scolaire':      forms.TextInput(attrs={'placeholder': 'Nom de l\'école ou établissement'}),
            'contact_urgence':    forms.TextInput(attrs={'placeholder': 'Nom & téléphone contact d\'urgence'}),
            'matchs_joues':       forms.NumberInput(attrs={'min': 0}),
            'buts':               forms.NumberInput(attrs={'min': 0}),
            'numero_licence':     forms.TextInput(attrs={'placeholder': 'Ex. FIF-2026-0001'}),
            'date_inscription':   forms.DateInput(attrs={'type': 'date'}),
        }
