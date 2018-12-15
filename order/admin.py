from django.contrib import admin
from .models import OrdineInAttesa, RichiedeP, RichiedeM


class OrdineInAttesaAdmin(admin.ModelAdmin):
    fieldsets = [('Dettagli Ordine', {'fields': ['data', 'metodo_pagamento', 'orario_richiesto']}),
                 ('Dettagli Persona', {'fields': ['email', 'cod_carta']}),
                 ]
    list_display = ['cod_ordine', 'data', 'metodo_pagamento', 'orario_richiesto', 'email']
    ordering = ['cod_ordine']


class RichiedeMAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['cod_ordine', 'cod_locale', 'nome_menu', 'quantita']}), ]
    list_display = ['cod_ordine', 'cod_locale', 'nome_menu', 'quantita']


class RichiedePAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['cod_ordine', 'cod_locale', 'nome_prodotto', 'quantita']}), ]
    list_display = ['cod_ordine', 'cod_locale', 'nome_prodotto', 'quantita']


admin.site.register(OrdineInAttesa, OrdineInAttesaAdmin)
admin.site.register(RichiedeM, RichiedeMAdmin)
admin.site.register(RichiedeP, RichiedePAdmin)
