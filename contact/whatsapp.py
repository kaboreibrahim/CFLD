import requests
from django.conf import settings


def envoyer_notification_whatsapp(message_obj):
    url = f"https://{settings.INFOBIP_BASE_URL}/whatsapp/1/message/text"
    headers = {
        "Authorization": f"App {settings.INFOBIP_API_KEY}",
        "Content-Type": "application/json",
    }
    texte = (
        f"📩 *Nouveau message de contact - CFLD*\n\n"
        f"*Nom :* {message_obj.nom}\n"
        f"*Email :* {message_obj.email}\n"
        f"*Sujet :* {message_obj.get_sujet_display()}\n"
        f"*Message :*\n{message_obj.message}\n\n"
        f"*Date :* {message_obj.date_envoi.strftime('%d/%m/%Y à %H:%M')}"
    )
    payload = {
        "messages": [
            {
                "from": settings.INFOBIP_WHATSAPP_SENDER,
                "to": settings.INFOBIP_ADMIN_PHONE,
                "content": {"text": texte},
            }
        ]
    }
    import logging
    logger = logging.getLogger(__name__)
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        logger.error("Infobip response [%s]: %s", response.status_code, response.text)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("Infobip WhatsApp error: %s", e)
