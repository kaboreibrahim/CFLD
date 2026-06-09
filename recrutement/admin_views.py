"""
Compatibilité : ce module re-exporte toutes les vues depuis recrutement/views/.
Les URLs (admin_urls.py) importent depuis ici via `from . import admin_views as v`.

Pour ajouter ou modifier une vue, éditez le fichier correspondant dans views/.
"""
from recrutement.views.admin_dashboard import admin_dashboard  # noqa: F401
from recrutement.views.admin_joueurs import (  # noqa: F401
    admin_joueur_delete,
    admin_joueur_detail,
    admin_joueur_form,
    admin_joueur_pdf,
    admin_joueurs,
    admin_joueurs_excel,
    admin_joueurs_pdf,
)
from recrutement.views.admin_matchs import (  # noqa: F401
    admin_classement,
    admin_classement_delete,
    admin_classement_form,
    admin_match_delete,
    admin_match_form,
    admin_matchs,
)
from recrutement.views.admin_medias import (  # noqa: F401
    admin_article_delete,
    admin_article_form,
    admin_articles,
    admin_photo_delete,
    admin_photo_form,
    admin_photos,
    admin_video_delete,
    admin_video_form,
    admin_videos,
)
from recrutement.views.admin_candidatures import (  # noqa: F401
    action_candidature,
    admin_candidatures,
    admin_migrer_acceptees,
    candidature_pdf_regenerer,
    candidature_pdf_telecharger,
    candidature_pdf_voir,
)
from recrutement.views.admin_messages import (  # noqa: F401
    admin_message_delete,
    admin_message_detail,
    admin_messages,
)
from recrutement.views.admin_ticker import (  # noqa: F401
    admin_ticker,
    admin_ticker_delete,
    admin_ticker_form,
)
from recrutement.views.admin_audit import (  # noqa: F401
    admin_audit,
    admin_audit_detail,
)
