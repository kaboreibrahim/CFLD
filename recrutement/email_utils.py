"""
Envoi d'emails CFLD pour les inscriptions.
"""
import os
from django.conf import settings
from django.core.mail import EmailMessage


def envoyer_confirmation_inscription(candidature):
    """Email de confirmation envoyé au candidat (ou parent) après soumission."""
    destinataires = [candidature.email]
    if candidature.email_parent:
        destinataires.append(candidature.email_parent)

    sujet = f'[CFLD] Confirmation de candidature — {candidature.reference}'
    corps = f"""Bonjour {candidature.prenom} {candidature.nom},

Nous avons bien reçu votre dossier de candidature au Centre de Formation Lancine Diomandé (CFLD).

Référence dossier : {candidature.reference}
Catégorie : {candidature.section}
Date de soumission : {candidature.date_soumission.strftime('%d/%m/%Y à %H:%M')}

Notre cellule technique étudiera votre dossier dans les meilleurs délais (généralement sous 72h).
Vous recevrez un email de confirmation dès qu'une décision sera prise.

Veuillez conserver cette référence pour tout échange avec notre staff.

Cordialement,
L'équipe du CFLD — Aboisso, Côte d'Ivoire
"""
    email = EmailMessage(
        subject=sujet,
        body=corps,
        from_email=settings.EMAIL_HOST_USER,
        to=destinataires,
    )
    if candidature.pdf_inscription:
        pdf_path = os.path.join(settings.MEDIA_ROOT, str(candidature.pdf_inscription))
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                email.attach(
                    f'inscription_{candidature.reference}.pdf',
                    f.read(),
                    'application/pdf',
                )
    try:
        email.send(fail_silently=True)
    except Exception:
        pass


def envoyer_validation_inscription(candidature):
    """Email envoyé au candidat lorsque sa candidature est validée."""
    destinataires = [candidature.email]
    if candidature.email_parent:
        destinataires.append(candidature.email_parent)

    sujet = f'[CFLD] Votre inscription est validée — {candidature.reference}'
    corps = f"""Bonjour {candidature.prenom} {candidature.nom},

Nous avons le plaisir de vous informer que votre inscription au CFLD a été VALIDÉE.

Référence dossier : {candidature.reference}
Section intégrée : {candidature.section}

Vous êtes désormais officiellement intégré(e) dans l'effectif du CFLD.
Notre staff vous contactera prochainement pour vous communiquer les modalités d'accueil.

Veuillez trouver ci-joint votre dossier d'inscription complet au format PDF.

Bienvenue dans la famille CFLD !

Cordialement,
L'équipe du CFLD — Aboisso, Côte d'Ivoire
"""
    email = EmailMessage(
        subject=sujet,
        body=corps,
        from_email=settings.EMAIL_HOST_USER,
        to=destinataires,
    )
    if candidature.pdf_inscription:
        pdf_path = os.path.join(settings.MEDIA_ROOT, str(candidature.pdf_inscription))
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                email.attach(
                    f'inscription_{candidature.reference}.pdf',
                    f.read(),
                    'application/pdf',
                )
    try:
        email.send(fail_silently=True)
    except Exception:
        pass


def envoyer_refus_inscription(candidature):
    """Email envoyé au candidat lorsque sa candidature est refusée."""
    destinataires = [candidature.email]
    if candidature.email_parent:
        destinataires.append(candidature.email_parent)

    sujet = f'[CFLD] Décision concernant votre dossier — {candidature.reference}'
    corps = f"""Bonjour {candidature.prenom} {candidature.nom},

Nous avons bien étudié votre dossier de candidature (réf. {candidature.reference}) et nous vous remercions de l'intérêt que vous portez au CFLD.

Après examen, il nous est malheureusement impossible de donner une suite favorable à votre candidature pour cette saison.

Cette décision ne remet pas en cause vos qualités sportives. Nous vous encourageons à continuer votre pratique et à vous représenter lors des prochaines détections.

Cordialement,
L'équipe du CFLD — Aboisso, Côte d'Ivoire
"""
    email = EmailMessage(
        subject=sujet,
        body=corps,
        from_email=settings.EMAIL_HOST_USER,
        to=destinataires,
    )
    try:
        email.send(fail_silently=True)
    except Exception:
        pass
