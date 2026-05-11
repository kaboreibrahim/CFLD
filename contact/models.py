from django.db import models
from django.utils import timezone


class Message(models.Model):
    SUJET_CHOICES = [
        ('info', 'Informations générales'),
        ('recrutement', 'Recrutement'),
        ('partenariat', 'Partenariat'),
        ('presse', 'Presse & médias'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=100)
    email = models.EmailField()
    sujet = models.CharField(max_length=15, choices=SUJET_CHOICES, default='info')
    message = models.TextField()
    date_envoi = models.DateTimeField(default=timezone.now)
    lu = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_envoi']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f"{self.nom} — {self.get_sujet_display()} ({self.date_envoi.strftime('%d/%m/%Y')})"
