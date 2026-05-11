from django.db import models


class InfoTicker(models.Model):
    TYPE_CHOICES = [
        ('score_live',     'Score en direct'),
        ('score_resultat', 'Résultat'),
        ('prochain_match', 'Prochain match'),
        ('annonce',        'Annonce'),
    ]

    type      = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Type')
    categorie = models.CharField(max_length=30, blank=True,
                                 help_text='Ex : U17, U15, Ligue 1 CI')
    equipe_dom = models.CharField(max_length=60, blank=True, verbose_name='Équipe domicile')
    equipe_ext = models.CharField(max_length=60, blank=True, verbose_name='Équipe extérieur')
    score_dom  = models.PositiveSmallIntegerField(null=True, blank=True,
                                                  verbose_name='Score dom.')
    score_ext  = models.PositiveSmallIntegerField(null=True, blank=True,
                                                  verbose_name='Score ext.')
    minute     = models.PositiveSmallIntegerField(null=True, blank=True,
                                                  help_text="Minute de jeu (score_live uniquement)")
    texte      = models.CharField(max_length=200, blank=True,
                                  help_text='Texte libre pour les types annonce / prochain_match')
    actif  = models.BooleanField(default=True)
    ordre  = models.PositiveSmallIntegerField(default=0,
                                              help_text='Ordre d\'affichage (croissant)')

    class Meta:
        ordering = ['ordre', 'pk']
        verbose_name = 'Info ticker'
        verbose_name_plural = 'Infos ticker'

    def __str__(self):
        if self.type in ('score_live', 'score_resultat'):
            cat = f'{self.categorie} · ' if self.categorie else ''
            return f'{cat}{self.equipe_dom} {self.score_dom}—{self.score_ext} {self.equipe_ext}'
        return self.texte[:80]
