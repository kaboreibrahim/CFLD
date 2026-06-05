from django.urls import path
from django.contrib.auth import views as auth_views
from . import admin_views as v
from payments import admin_views as pv

urlpatterns = [
    # Auth
    path('login/',  auth_views.LoginView.as_view(template_name='recrutement/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Dashboard
    path('', v.admin_dashboard, name='admin_dashboard'),

    # Joueurs
    path('joueurs/',                    v.admin_joueurs,       name='admin_joueurs'),
    path('joueurs/ajouter/',            v.admin_joueur_form,   name='admin_joueur_add'),
    path('joueurs/pdf/',                v.admin_joueurs_pdf,   name='admin_joueurs_pdf'),
    path('joueurs/excel/',              v.admin_joueurs_excel, name='admin_joueurs_excel'),
    path('joueurs/<int:pk>/',           v.admin_joueur_form,   name='admin_joueur_edit'),
    path('joueurs/<int:pk>/detail/',    v.admin_joueur_detail, name='admin_joueur_detail'),
    path('joueurs/<int:pk>/supprimer/', v.admin_joueur_delete, name='admin_joueur_delete'),
    path('joueurs/<int:pk>/pdf/',       v.admin_joueur_pdf,    name='admin_joueur_pdf'),

    # Matchs
    path('matchs/',                   v.admin_matchs,       name='admin_matchs'),
    path('matchs/ajouter/',           v.admin_match_form,   name='admin_match_add'),
    path('matchs/<int:pk>/',          v.admin_match_form,   name='admin_match_edit'),
    path('matchs/<int:pk>/supprimer/', v.admin_match_delete, name='admin_match_delete'),

    # Classement
    path('classement/',                   v.admin_classement,       name='admin_classement'),
    path('classement/ajouter/',           v.admin_classement_form,  name='admin_classement_add'),
    path('classement/<int:pk>/',          v.admin_classement_form,  name='admin_classement_edit'),
    path('classement/<int:pk>/supprimer/', v.admin_classement_delete, name='admin_classement_delete'),

    # Articles
    path('articles/',                   v.admin_articles,      name='admin_articles'),
    path('articles/ajouter/',           v.admin_article_form,  name='admin_article_add'),
    path('articles/<int:pk>/',          v.admin_article_form,  name='admin_article_edit'),
    path('articles/<int:pk>/supprimer/', v.admin_article_delete, name='admin_article_delete'),

    # Photos
    path('photos/',                   v.admin_photos,      name='admin_photos'),
    path('photos/ajouter/',           v.admin_photo_form,  name='admin_photo_add'),
    path('photos/<int:pk>/',          v.admin_photo_form,  name='admin_photo_edit'),
    path('photos/<int:pk>/supprimer/', v.admin_photo_delete, name='admin_photo_delete'),

    # Vidéos
    path('videos/',                   v.admin_videos,      name='admin_videos'),
    path('videos/ajouter/',           v.admin_video_form,  name='admin_video_add'),
    path('videos/<int:pk>/',          v.admin_video_form,  name='admin_video_edit'),
    path('videos/<int:pk>/supprimer/', v.admin_video_delete, name='admin_video_delete'),

    # Candidatures
    path('candidatures/',                            v.admin_candidatures,           name='admin_candidatures'),
    path('candidatures/migrer-acceptees/',           v.admin_migrer_acceptees,       name='admin_migrer_acceptees'),
    path('candidature/<int:pk>/action/',             v.action_candidature,           name='action_candidature'),
    path('candidature/<int:pk>/pdf/telecharger/',    v.candidature_pdf_telecharger,  name='candidature_pdf_telecharger'),
    path('candidature/<int:pk>/pdf/voir/',           v.candidature_pdf_voir,         name='candidature_pdf_voir'),
    path('candidature/<int:pk>/pdf/regenerer/',      v.candidature_pdf_regenerer,    name='candidature_pdf_regenerer'),

    # Messages
    path('messages/',                   v.admin_messages,       name='admin_messages'),
    path('messages/<int:pk>/',          v.admin_message_detail, name='admin_message_detail'),
    path('messages/<int:pk>/supprimer/', v.admin_message_delete, name='admin_message_delete'),

    # Ticker
    path('ticker/',                   v.admin_ticker,       name='admin_ticker'),
    path('ticker/ajouter/',           v.admin_ticker_form,  name='admin_ticker_add'),
    path('ticker/<int:pk>/',          v.admin_ticker_form,  name='admin_ticker_edit'),
    path('ticker/<int:pk>/supprimer/', v.admin_ticker_delete, name='admin_ticker_delete'),

    # Paiements — Comptes
    path('paiements/comptes/',                        pv.admin_comptes_paiement,        name='admin_comptes_paiement'),
    path('paiements/comptes/ajouter/',                pv.admin_compte_paiement_form,    name='admin_compte_paiement_add'),
    path('paiements/comptes/<uuid:pk>/',              pv.admin_compte_paiement_form,    name='admin_compte_paiement_edit'),
    path('paiements/comptes/<uuid:pk>/supprimer/',    pv.admin_compte_paiement_delete,  name='admin_compte_paiement_delete'),

    # Paiements — Visite médicale
    path('paiements/visite/',                         pv.admin_paiements_visite,         name='admin_paiements_visite'),
    path('paiements/visite/ajouter/',                 pv.admin_paiement_visite_form,     name='admin_paiement_visite_add'),
    path('paiements/visite/<uuid:pk>/',               pv.admin_paiement_visite_form,     name='admin_paiement_visite_edit'),
    path('paiements/visite/<uuid:pk>/action/',        pv.admin_paiement_visite_action,   name='admin_paiement_visite_action'),
    path('paiements/visite/<uuid:pk>/pdf/',           pv.admin_visite_pdf,               name='admin_visite_pdf'),

    # Paiements — Inscription
    path('paiements/inscription/',                    pv.admin_paiements_inscription,       name='admin_paiements_inscription'),
    path('paiements/inscription/ajouter/',            pv.admin_paiement_inscription_form,   name='admin_paiement_inscription_add'),
    path('paiements/inscription/<uuid:pk>/',          pv.admin_paiement_inscription_form,   name='admin_paiement_inscription_edit'),
    path('paiements/inscription/<uuid:pk>/action/',   pv.admin_paiement_inscription_action, name='admin_paiement_inscription_action'),

    # Paiements — Cotisations annuelles
    path('paiements/cotisations/',                            pv.admin_cotisations_dashboard,  name='admin_cotisations_dashboard'),
    path('paiements/cotisations/creer/',                      pv.admin_cotisation_creer,       name='admin_cotisation_creer'),
    path('paiements/cotisations/creer-tous/',                 pv.admin_cotisation_creer_tous,  name='admin_cotisation_creer_tous'),
    path('paiements/cotisations/<uuid:pk>/',                  pv.admin_cotisation_detail,      name='admin_cotisation_detail'),
    path('paiements/cotisations/<uuid:cotisation_pk>/versement/', pv.admin_versement_add, name='admin_versement_add'),
    path('paiements/cotisations/versement/<uuid:pk>/action/', pv.admin_versement_action,       name='admin_versement_action'),
    path('paiements/cotisations/versement/<uuid:pk>/pdf/',    pv.admin_versement_pdf,          name='admin_versement_pdf'),

    # Paiements — Inscription détail & PDF
    path('paiements/inscription/<uuid:pk>/detail/', pv.admin_inscription_detail, name='admin_inscription_detail'),
    path('paiements/inscription/<uuid:pk>/pdf/',    pv.admin_inscription_pdf,    name='admin_inscription_pdf'),
]
