from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'sujet', 'date_envoi', 'lu']
    list_filter = ['sujet', 'lu']
    search_fields = ['nom', 'email', 'message']
    list_editable = ['lu']
    readonly_fields = ['date_envoi']
