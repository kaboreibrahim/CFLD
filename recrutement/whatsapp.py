import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _post(to, texte):
    url = f"https://{settings.INFOBIP_BASE_URL}/whatsapp/1/message/text"
    headers = {
        "Authorization": f"App {settings.INFOBIP_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "messages": [
            {
                "from": settings.INFOBIP_WHATSAPP_SENDER,
                "to": to,
                "content": {"text": texte},
            }
        ]
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        logger.info("Infobip [%s] -> %s : %s", response.status_code, to, response.text)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("Infobip WhatsApp error: %s", e)


def notifier_admin(candidature):
    texte = (
        f"⚽ *Nouvelle candidature CFLD*\n\n"
        f"*Réf :* {candidature.reference}\n"
        f"*Joueur :* {candidature.nom_complet}\n"
        f"*Poste :* {candidature.get_poste_display()}\n"
        f"*Âge :* {candidature.age} ans\n"
        f"*Nationalité :* {candidature.nationalite}\n"
        f"*Ancien club :* {candidature.ancien_club or '—'}\n"
        f"*WhatsApp :* {candidature.telephone_whatsapp}\n"
        f"*Email :* {candidature.email}\n"
        f"*Date :* {candidature.date_soumission.strftime('%d/%m/%Y à %H:%M')}"
    )
    _post(settings.INFOBIP_ADMIN_PHONE, texte)


def confirmer_candidat(candidature):
    telephone = candidature.telephone_whatsapp.strip().replace(' ', '').replace('+', '')
    texte = (
        f"Bonjour {candidature.prenom},\n\n"
        f"Votre candidature au *CFLD* a bien été reçue ✅\n\n"
        f"*Référence :* {candidature.reference}\n"
        f"*Poste :* {candidature.get_poste_display()}\n\n"
        f"Notre staff examinera votre dossier et vous contactera prochainement.\n\n"
        f"Merci pour votre intérêt — *Club de Football Les Déterminés*"
    )
    _post(telephone, texte)
