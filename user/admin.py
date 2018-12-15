from django.contrib import admin
from .models import Recensione, CartaDiCredito


class CartaDiCreditoAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['numero_carta', 'intestatario', 'scadenza']})]
    list_display = ['numero_carta', 'intestatario', 'scadenza']


class RecensioniAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['voto', 'descrizione', 'date', 'cod_locale']}),
                 ('Altre info', {'fields': ['email', 'p_iva']}),
                 ]
    list_display = ['cod_recensione', 'voto', 'descrizione', 'email', 'p_iva', 'date', 'cod_locale']
    list_select_related = ['cod_locale', 'email', 'p_iva']
    ordering = ['email', 'cod_locale', 'cod_recensione']


admin.site.register(CartaDiCredito, CartaDiCreditoAdmin)
admin.site.register(Recensione, RecensioniAdmin)
