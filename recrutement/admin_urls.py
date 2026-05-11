from django.urls import path
from django.contrib.auth import views as auth_views
from . import admin_views as v

urlpatterns = [
    # Auth
    path('login/',  auth_views.LoginView.as_view(template_name='recrutement/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Dashboard
    path('', v.admin_dashboard, name='admin_dashboard'),

    # Joueurs
    path('joueurs/',                  v.admin_joueurs,       name='admin_joueurs'),
    path('joueurs/ajouter/',          v.admin_joueur_form,   name='admin_joueur_add'),
    path('joueurs/<int:pk>/',         v.admin_joueur_form,   name='admin_joueur_edit'),
    path('joueurs/<int:pk>/supprimer/', v.admin_joueur_delete, name='admin_joueur_delete'),

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
    path('candidatures/',                       v.admin_candidatures,  name='admin_candidatures'),
    path('candidature/<int:pk>/action/',        v.action_candidature,  name='action_candidature'),

    # Messages
    path('messages/',                   v.admin_messages,       name='admin_messages'),
    path('messages/<int:pk>/',          v.admin_message_detail, name='admin_message_detail'),
    path('messages/<int:pk>/supprimer/', v.admin_message_delete, name='admin_message_delete'),

    # Ticker
    path('ticker/',                   v.admin_ticker,       name='admin_ticker'),
    path('ticker/ajouter/',           v.admin_ticker_form,  name='admin_ticker_add'),
    path('ticker/<int:pk>/',          v.admin_ticker_form,  name='admin_ticker_edit'),
    path('ticker/<int:pk>/supprimer/', v.admin_ticker_delete, name='admin_ticker_delete'),
]
