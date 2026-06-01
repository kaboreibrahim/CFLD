from django.db import models


class Joueur(models.Model):
    POSTE_CHOICES = [
        ('GK', 'Gardien'),
        ('DEF', 'Défenseur'),
        ('MIL', 'Milieu'),
        ('ATT', 'Attaquant'),
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

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numero = models.PositiveSmallIntegerField()
    poste = models.CharField(max_length=3, choices=POSTE_CHOICES)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, default='M')
    categorie = models.CharField(max_length=4, choices=CATEGORIE_CHOICES, default='U13')
    age = models.PositiveSmallIntegerField()
    matchs_joues = models.PositiveSmallIntegerField(default=0)
    buts = models.PositiveSmallIntegerField(default=0)
    nationalite = models.CharField(max_length=60, default="Côte d'Ivoire")
    numero_licence = models.CharField(max_length=50, blank=True)
    date_inscription = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='effectif/', blank=True, null=True)
    actif = models.BooleanField(default=True)
    candidature = models.OneToOneField(
        'recrutement.Candidature',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='joueur',
    )

    class Meta:
        ordering = ['categorie', 'sexe', 'poste', 'numero']
        verbose_name = 'Joueur'
        verbose_name_plural = 'Joueurs'

    def __str__(self):
        return f"{self.numero} — {self.prenom} {self.nom} ({self.categorie} {self.get_sexe_display()})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @property
    def section(self):
        sexe_label = 'Masculin' if self.sexe == 'M' else 'Féminin'
        return f"{self.categorie} {sexe_label}"
