from django import forms
from .models import (
    ComptePaiement, PaiementVisiteMedicale, PaiementInscription,
    CotisationAnnuelle, VersementCotisation,
    MONTANT_TOTAL_DEFAUT, MONTANT_PREMIER_VERSEMENT, MONTANT_MENSUEL,
)
from effectif.models import Joueur
from recrutement.models import Candidature


class ComptePaiementForm(forms.ModelForm):
    class Meta:
        model = ComptePaiement
        fields = [
            'mode', 'numero', 'nom_titulaire', 'qr_code',
            'instructions', 'est_actif', 'ordre_affichage',
        ]
        widgets = {
            'mode': forms.Select(attrs={'class': 'fi-select'}),
            'numero': forms.TextInput(attrs={'class': 'fi-input', 'placeholder': 'Ex: 07 07 07 07 07'}),
            'nom_titulaire': forms.TextInput(attrs={'class': 'fi-input', 'placeholder': 'Nom du titulaire du compte'}),
            'instructions': forms.Textarea(attrs={'class': 'fi-input', 'rows': 3, 'placeholder': 'Instructions pour le paiement (facultatif)'}),
            'ordre_affichage': forms.NumberInput(attrs={'class': 'fi-input', 'min': 0}),
        }


class PaiementVisiteForm(forms.ModelForm):
    class Meta:
        model = PaiementVisiteMedicale
        fields = [
            'candidature', 'montant',
            'compte_paiement', 'reference_transaction',
            'capture_depot', 'date_paiement', 'notes',
        ]
        widgets = {
            'candidature': forms.Select(attrs={'class': 'fi-select'}),
            'montant': forms.NumberInput(attrs={'class': 'fi-input', 'placeholder': 'Ex: 5000', 'min': 1}),
            'compte_paiement': forms.Select(attrs={'class': 'fi-select'}),
            'reference_transaction': forms.TextInput(attrs={'class': 'fi-input', 'placeholder': 'Référence/ID visible sur la capture'}),
            'date_paiement': forms.DateInput(attrs={'class': 'fi-input', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'fi-input', 'rows': 3, 'placeholder': 'Notes internes (facultatif)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['compte_paiement'].queryset = ComptePaiement.objects.filter(est_actif=True)
        self.fields['compte_paiement'].empty_label = '— Choisir le numéro de dépôt —'
        self.fields['candidature'].queryset = Candidature.objects.order_by('-date_soumission')
        self.fields['candidature'].empty_label = '— Sélectionner une candidature —'


class PaiementInscriptionForm(forms.ModelForm):
    class Meta:
        model = PaiementInscription
        fields = [
            'candidature', 'montant',
            'compte_paiement', 'reference_transaction',
            'capture_depot', 'date_paiement', 'notes',
        ]
        widgets = {
            'candidature': forms.Select(attrs={'class': 'fi-select'}),
            'montant': forms.NumberInput(attrs={'class': 'fi-input', 'placeholder': 'Ex: 10000', 'min': 1}),
            'compte_paiement': forms.Select(attrs={'class': 'fi-select'}),
            'reference_transaction': forms.TextInput(attrs={'class': 'fi-input', 'placeholder': 'Référence/ID visible sur la capture'}),
            'date_paiement': forms.DateInput(attrs={'class': 'fi-input', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'fi-input', 'rows': 3, 'placeholder': 'Notes internes (facultatif)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['compte_paiement'].queryset = ComptePaiement.objects.filter(est_actif=True)
        self.fields['compte_paiement'].empty_label = '— Choisir le numéro de dépôt —'
        self.fields['candidature'].empty_label = '— Sélectionner une candidature —'
        self.fields['candidature'].queryset = Candidature.objects.order_by('-date_soumission')


class CotisationAnnuelleForm(forms.ModelForm):
    class Meta:
        model = CotisationAnnuelle
        fields = ['joueur', 'annee', 'montant_total', 'statut', 'notes']
        widgets = {
            'joueur': forms.Select(attrs={'class': 'fi-select'}),
            'annee': forms.NumberInput(attrs={'class': 'fi-input', 'min': 2020, 'max': 2100}),
            'montant_total': forms.NumberInput(attrs={'class': 'fi-input', 'min': 1}),
            'statut': forms.Select(attrs={'class': 'fi-select'}),
            'notes': forms.Textarea(attrs={'class': 'fi-input', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['joueur'].queryset = Joueur.objects.filter(actif=True).order_by('nom', 'prenom')
        self.fields['joueur'].empty_label = '— Sélectionner un joueur —'


class VersementForm(forms.ModelForm):
    class Meta:
        model = VersementCotisation
        fields = [
            'type_versement', 'montant',
            'compte_paiement', 'reference_transaction',
            'capture_depot', 'date_versement', 'notes',
        ]
        widgets = {
            'type_versement': forms.Select(attrs={'class': 'fi-select'}),
            'montant': forms.NumberInput(attrs={'class': 'fi-input', 'min': 1}),
            'compte_paiement': forms.Select(attrs={'class': 'fi-select'}),
            'reference_transaction': forms.TextInput(attrs={'class': 'fi-input', 'placeholder': 'Référence visible sur la capture'}),
            'date_versement': forms.DateInput(attrs={'class': 'fi-input', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'fi-input', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['compte_paiement'].queryset = ComptePaiement.objects.filter(est_actif=True)
        self.fields['compte_paiement'].empty_label = '— Choisir le numéro de dépôt —'
