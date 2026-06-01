from django.db import models


class SEOPage(models.Model):
    """Paramètres SEO gérés par les administrateurs pour chaque page du site."""

    INDEXATION_CHOICES = [
        ('index, follow', 'Indexer (recommandé)'),
        ('noindex, nofollow', 'Ne pas indexer'),
        ('index, nofollow', 'Indexer sans suivre les liens'),
        ('noindex, follow', 'Ne pas indexer, suivre les liens'),
    ]

    page_id = models.CharField(
        max_length=80, unique=True,
        help_text='Identifiant unique de la page (ex: accueil, club, academie…)',
    )
    titre_seo = models.CharField(max_length=70, blank=True, help_text='Titre affiché dans Google (max 70 car.)')
    meta_description = models.CharField(max_length=160, blank=True, help_text='Description dans les résultats Google (max 160 car.)')
    mots_cles = models.CharField(max_length=300, blank=True, help_text='Mots-clés séparés par des virgules')
    image_sociale = models.ImageField(upload_to='seo/og_images/', blank=True, null=True, help_text='Image Open Graph / Twitter Card (1200×630 px)')
    indexation = models.CharField(max_length=30, choices=INDEXATION_CHOICES, default='index, follow')
    slug_personnalise = models.CharField(max_length=100, blank=True, help_text='Laisser vide pour utiliser l\'URL par défaut')
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['page_id']
        verbose_name = 'Page SEO'
        verbose_name_plural = 'Pages SEO'

    def __str__(self):
        return f"SEO — {self.page_id}"

    @property
    def robots(self):
        return self.indexation
