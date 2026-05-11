from django.db import models


class Match(models.Model):
    TYPE_CHOICES = [
        ('a_venir', 'À venir'),
        ('resultat', 'Résultat'),
    ]

    equipe_domicile = models.CharField(max_length=100)
    equipe_exterieur = models.CharField(max_length=100)
    est_domicile = models.BooleanField(
        default=True,
        help_text="CFLD joue à domicile ?"
    )
    score_domicile = models.PositiveSmallIntegerField(null=True, blank=True)
    score_exterieur = models.PositiveSmallIntegerField(null=True, blank=True)
    date = models.DateTimeField()
    lieu = models.CharField(max_length=150, blank=True)
    competition = models.CharField(max_length=100, default='Ligue 1 CI')
    journee = models.PositiveSmallIntegerField(null=True, blank=True)
    type_match = models.CharField(max_length=10, choices=TYPE_CHOICES, default='a_venir')
    billet_url = models.URLField(blank=True)

    class Meta:
        ordering = ['date']
        verbose_name = 'Match'
        verbose_name_plural = 'Matchs'

    def __str__(self):
        return f"{self.equipe_domicile} vs {self.equipe_exterieur} — {self.date.strftime('%d/%m/%Y')}"

    @property
    def resultat(self):
        if self.score_domicile is None:
            return None
        if self.score_domicile > self.score_exterieur:
            return 'V' if self.est_domicile else 'D'
        if self.score_domicile < self.score_exterieur:
            return 'D' if self.est_domicile else 'V'
        return 'N'


class Classement(models.Model):
    equipe = models.CharField(max_length=100)
    points = models.PositiveSmallIntegerField(default=0)
    matchs_joues = models.PositiveSmallIntegerField(default=0)
    victoires = models.PositiveSmallIntegerField(default=0)
    nuls = models.PositiveSmallIntegerField(default=0)
    defaites = models.PositiveSmallIntegerField(default=0)
    buts_pour = models.PositiveSmallIntegerField(default=0)
    buts_contre = models.PositiveSmallIntegerField(default=0)
    est_cfld = models.BooleanField(default=False)
    saison = models.CharField(max_length=20, default='2025-2026')

    class Meta:
        ordering = ['-points', '-buts_pour']
        verbose_name = 'Classement'
        verbose_name_plural = 'Classements'

    def __str__(self):
        return f"{self.equipe} — {self.points} pts"

    @property
    def difference_buts(self):
        return self.buts_pour - self.buts_contre
