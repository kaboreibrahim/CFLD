"""
Compatibilité : ce module re-exporte toutes les vues admin depuis payments/views/.
Les URLs (recrutement/admin_urls.py) importent ici via `from payments import admin_views as pv`.

Pour modifier une vue, éditez le fichier correspondant dans views/.
"""
from payments.views.admin_comptes import (  # noqa: F401
    admin_compte_paiement_delete,
    admin_compte_paiement_form,
    admin_comptes_paiement,
)
from payments.views.admin_visite import (  # noqa: F401
    admin_paiement_visite_action,
    admin_paiement_visite_form,
    admin_paiements_visite,
)
from payments.views.admin_inscription import (  # noqa: F401
    admin_inscription_detail,
    admin_inscription_pdf,
    admin_paiement_inscription_action,
    admin_paiement_inscription_form,
    admin_paiements_inscription,
)
from payments.views.admin_cotisations import (  # noqa: F401
    admin_cotisation_creer,
    admin_cotisation_creer_tous,
    admin_cotisation_detail,
    admin_cotisations_dashboard,
    admin_versement_action,
    admin_versement_add,
)
from payments.views.admin_pdf import (  # noqa: F401
    admin_versement_pdf,
    admin_visite_pdf,
)
