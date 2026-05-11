from django.db import models


class Joueur(models.Model):
    POSTE_CHOICES = [
        ('GK', 'Gardien'),
        ('DEF', 'Défenseur'),
        ('MIL', 'Milieu'),
        ('ATT', 'Attaquant'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numero = models.PositiveSmallIntegerField()
    poste = models.CharField(max_length=3, choices=POSTE_CHOICES)
    age = models.PositiveSmallIntegerField()
    matchs_joues = models.PositiveSmallIntegerField(default=0)
    buts = models.PositiveSmallIntegerField(default=0)
    nationalite = models.CharField(max_length=60, default="Côte d'Ivoire")
    photo = models.ImageField(upload_to='effectif/', blank=True, null=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['poste', 'numero']
        verbose_name = 'Joueur'
        verbose_name_plural = 'Joueurs'

    def __str__(self):
        return f"{self.numero} — {self.prenom} {self.nom} ({self.poste})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"
