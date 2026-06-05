import random
import string
from django.db import models
from django.utils import timezone


def generer_reference():
    return 'CFLD-' + ''.join(random.choices(string.digits, k=6))


class Candidature(models.Model):
    STATUT_CHOICES = [
        ('pending', 'En attente'),
        ('waiting', 'Mise en attente'),
        ('accepted', 'Acceptée'),
        ('refused', 'Refusée'),
    ]

    POSTE_CHOICES = [
        ('GK', 'Gardien'),
        ('DC', 'Déf. Central'),
        ('LAT', 'Latéral'),
        ('MD', 'Milieu Déf.'),
        ('MO', 'Milieu Off.'),
        ('AIL', 'Ailier'),
        ('ATT', 'Attaquant'),
        ('OTH', 'Autre'),
    ]

    PIED_CHOICES = [
        ('Droit', 'Droit'),
        ('Gauche', 'Gauche'),
        ('Ambidextre', 'Ambidextre'),
    ]

    NATIONALITE_CHOICES = [
        ("Côte d'Ivoire", "Côte d'Ivoire"),
        ('Burkina Faso', 'Burkina Faso'),
        ('Mali', 'Mali'),
        ('Sénégal', 'Sénégal'),
        ('Ghana', 'Ghana'),
        ('Autre', 'Autre'),
    ]

    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    CATEGORIE_CHOICES = [
        ('U10', 'U10'),
        ('U12', 'U12'),
        ('U13', 'U13'),
        ('U15', 'U15'),
        ('U17+', 'U17+'),
    ]

    reference = models.CharField(max_length=20, unique=True, default=generer_reference, editable=False)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, default='M')
    categorie = models.CharField(max_length=4, choices=CATEGORIE_CHOICES, default='U13')
    nationalite = models.CharField(max_length=50, choices=NATIONALITE_CHOICES)
    poste = models.CharField(max_length=3, choices=POSTE_CHOICES)
    numero_prefere = models.PositiveSmallIntegerField(null=True, blank=True)
    pied_fort = models.CharField(max_length=12, choices=PIED_CHOICES)
    ancien_club = models.CharField(max_length=100, blank=True)
    telephone_whatsapp = models.CharField(max_length=30)
    email = models.EmailField()
    adresse = models.CharField(max_length=200, blank=True)
    # Parent / tuteur légal
    nom_parent = models.CharField(max_length=150, blank=True, verbose_name='Nom du parent/tuteur')
    telephone_parent = models.CharField(max_length=30, blank=True, verbose_name='Téléphone du parent/tuteur')
    email_parent = models.EmailField(blank=True, verbose_name='Email du parent/tuteur')
    # Infos complémentaires
    info_scolaire = models.CharField(max_length=200, blank=True, verbose_name='École / Établissement')
    contact_urgence = models.CharField(max_length=150, blank=True, verbose_name='Contact d\'urgence (nom & téléphone)')
    photo = models.ImageField(upload_to='candidatures/', blank=True, null=True)
    pdf_inscription = models.FileField(upload_to='inscriptions_pdf/', blank=True, null=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='pending')
    date_soumission = models.DateTimeField(default=timezone.now)
    note_interne = models.TextField(blank=True)
    notifie = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_soumission']
        verbose_name = 'Candidature'
        verbose_name_plural = 'Candidatures'

    def __str__(self):
        return f"{self.reference} — {self.prenom} {self.nom}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_naissance.year - (
            (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
        )

    @property
    def initiales(self):
        return (self.prenom[0] + self.nom[0]).upper()

    @property
    def section(self):
        sexe_label = 'Masculin' if self.sexe == 'M' else 'Féminin'
        return f"{self.categorie} {sexe_label}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.statut == 'accepted':
            self.creer_ou_mettre_a_jour_joueur()

    def creer_ou_mettre_a_jour_joueur(self):
        from django.db.models import Max
        from django.utils import timezone
        from effectif.models import Joueur

        numero = self.numero_prefere
        if numero is None:
            dernier_numero = (
                Joueur.objects
                .filter(categorie=self.categorie, sexe=self.sexe)
                .aggregate(max_numero=Max('numero'))['max_numero']
            )
            numero = (dernier_numero or 0) + 1

        Joueur.objects.update_or_create(
            candidature=self,
            defaults={
                'nom': self.nom,
                'prenom': self.prenom,
                'date_naissance': self.date_naissance,
                'sexe': self.sexe,
                'categorie': self.categorie,
                'nationalite': self.nationalite,
                'adresse': self.adresse,
                'numero': numero,
                'poste': self.poste,
                'pied_fort': self.pied_fort,
                'ancien_club': self.ancien_club,
                'age': self.age,
                'telephone_whatsapp': self.telephone_whatsapp,
                'email': self.email,
                'nom_parent': self.nom_parent,
                'telephone_parent': self.telephone_parent,
                'email_parent': self.email_parent,
                'info_scolaire': self.info_scolaire,
                'contact_urgence': self.contact_urgence,
                'date_inscription': timezone.localdate(),
                'photo': self.photo,
                'actif': True,
            },
        )
