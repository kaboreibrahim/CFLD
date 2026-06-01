from django.db import models


class Joueur(models.Model):
    POSTE_CHOICES = [
        ('GK',  'Gardien'),
        ('DC',  'Déf. Central'),
        ('LAT', 'Latéral'),
        ('MD',  'Milieu Déf.'),
        ('MO',  'Milieu Off.'),
        ('AIL', 'Ailier'),
        ('ATT', 'Attaquant'),
        ('OTH', 'Autre'),
    ]

    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    CATEGORIE_CHOICES = [
        ('U10',  'U10'),
        ('U12',  'U12'),
        ('U13',  'U13'),
        ('U15',  'U15'),
        ('U17+', 'U17+'),
    ]

    NATIONALITE_CHOICES = [
        ("Côte d'Ivoire", "Côte d'Ivoire"),
        ('Burkina Faso',  'Burkina Faso'),
        ('Mali',          'Mali'),
        ('Sénégal',       'Sénégal'),
        ('Ghana',         'Ghana'),
        ('Autre',         'Autre'),
    ]

    PIED_CHOICES = [
        ('Droit',       'Droit'),
        ('Gauche',      'Gauche'),
        ('Ambidextre',  'Ambidextre'),
    ]

    # ── Identité ─────────────────────────────────────────────────
    nom    = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)
    sexe       = models.CharField(max_length=1, choices=SEXE_CHOICES, default='M')
    categorie  = models.CharField(max_length=4, choices=CATEGORIE_CHOICES, default='U13')
    nationalite = models.CharField(max_length=60, choices=NATIONALITE_CHOICES, default="Côte d'Ivoire")
    adresse    = models.CharField(max_length=200, blank=True)

    # ── Profil sportif ───────────────────────────────────────────
    numero     = models.PositiveSmallIntegerField()
    poste      = models.CharField(max_length=3, choices=POSTE_CHOICES)
    pied_fort  = models.CharField(max_length=12, choices=PIED_CHOICES, blank=True)
    ancien_club = models.CharField(max_length=100, blank=True)
    age        = models.PositiveSmallIntegerField(default=0)

    # ── Contact joueur ───────────────────────────────────────────
    telephone_whatsapp = models.CharField(max_length=30, blank=True)
    email              = models.EmailField(blank=True)

    # ── Parent / tuteur ──────────────────────────────────────────
    nom_parent       = models.CharField(max_length=150, blank=True)
    telephone_parent = models.CharField(max_length=30, blank=True)
    email_parent     = models.EmailField(blank=True)

    # ── Infos complémentaires ────────────────────────────────────
    info_scolaire   = models.CharField(max_length=200, blank=True)
    contact_urgence = models.CharField(max_length=150, blank=True)

    # ── Stats & admin ────────────────────────────────────────────
    matchs_joues    = models.PositiveSmallIntegerField(default=0)
    buts            = models.PositiveSmallIntegerField(default=0)
    numero_licence  = models.CharField(max_length=50, blank=True)
    date_inscription = models.DateField(null=True, blank=True)
    photo  = models.ImageField(upload_to='effectif/', blank=True, null=True)
    actif  = models.BooleanField(default=True)
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
