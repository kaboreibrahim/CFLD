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

    reference = models.CharField(max_length=20, unique=True, default=generer_reference, editable=False)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    nationalite = models.CharField(max_length=50, choices=NATIONALITE_CHOICES)
    poste = models.CharField(max_length=3, choices=POSTE_CHOICES)
    numero_prefere = models.PositiveSmallIntegerField(null=True, blank=True)
    pied_fort = models.CharField(max_length=12, choices=PIED_CHOICES)
    ancien_club = models.CharField(max_length=100, blank=True)
    telephone_whatsapp = models.CharField(max_length=30)
    email = models.EmailField()
    adresse = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to='candidatures/', blank=True, null=True)
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
