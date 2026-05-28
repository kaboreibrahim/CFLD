from django.db import models
from django.utils import timezone


class Article(models.Model):
    CATEGORIE_CHOICES = [
        ('academie', 'Académie'),
        ('club', 'Club'),
        ('joueur', 'Joueur'),
        ('match', 'Match'),
        ('evenement', 'Événement'),
    ]

    titre = models.CharField(max_length=200)
    accroche = models.CharField(max_length=300, blank=True)
    contenu = models.TextField()
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, default='club')
    date_publication = models.DateTimeField(default=timezone.now)
    en_une = models.BooleanField(default=False)
    publie = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_publication']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __str__(self):
        return self.titre


class Photo(models.Model):
    legende = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='galerie/')
    auteur = models.CharField(max_length=100, blank=True, verbose_name='Auteur / Photographe')
    date = models.DateField(default=timezone.now)
    afficher = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'

    def __str__(self):
        return self.legende or f"Photo {self.pk}"


class Video(models.Model):
    TYPE_CHOICES = [
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
        ('local', 'Fichier local'),
    ]

    titre = models.CharField(max_length=200)
    description = models.CharField(max_length=300, blank=True)
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True, null=True)
    url = models.URLField(blank=True)
    type_video = models.CharField(max_length=10, choices=TYPE_CHOICES, default='youtube')
    date = models.DateField(default=timezone.now)
    afficher = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Vidéo'
        verbose_name_plural = 'Vidéos'

    def __str__(self):
        return self.titre
