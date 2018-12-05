from django.contrib import admin
# Register your models here.
from localManagement.models import *


class LocalitaInline(admin.StackedInline):
    model = Locale
    extra = 1


class TInLine(admin.StackedInline):
    model = Locale.tag.through
    extra = 1


class MenuInLine(admin.StackedInline):
    model = CompostoDa
    extra = 2


class ProdInLine(admin.StackedInline):
    model = CompostoDa
    extra = 1


class FotoInLine(admin.StackedInline):
    model = FotoLocale
    extra = 1


class ChiusuraInLine(admin.StackedInline):
    model = Chiusura
    extra = 1


class LocalitaAdmin(admin.ModelAdmin):
    fieldsets = [('Luogo', {'fields': ['cap', 'nome_localita']}), ]
    list_display = ('cap', 'nome_localita')
    search_fields = ['nome_localita__icontains']
    inlines = [LocalitaInline]
    ordering = ['nome_localita']


class LocaleAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['nome_locale']}),
                 ('About it', {'fields': ['descrizione', 'telefono', 'sito_web', 'email']}),
                 ('Orario', {'fields': ['orario_apertura', 'orario_chiusura']}),
                 ('Luogo', {'fields': ['cap', 'via', 'num_civico']}),
                 ]
    list_display = ('nome_locale', 'orario_apertura', 'orario_chiusura', 'cap', 'via', 'num_civico')
    list_display_links = ['nome_locale']
    list_select_related = (
        'cap',
    )
    search_fields = ['nome_locale']
    list_filter = ['orario_apertura', 'orario_chiusura']
    inlines = [FotoInLine, ChiusuraInLine, TInLine]


class TagAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['nome_tag']}), ]
    list_display = ['nome_tag']
    ordering = ['nome_tag']


class ProdottoAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['nome_prodotto', 'foto_prodotto']}),
                 ('About it', {'fields': ['descrizione_prodotto', 'prezzo', 'nome_tipo', 'cod_locale']}),
                 ]
    list_display = ['nome_prodotto', 'foto_prodotto', 'descrizione_prodotto', 'prezzo', 'nome_tipo']
    list_select_related = [
        'nome_tipo', 'cod_locale'
    ]
    inlines = [ProdInLine]


class MenuAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['nome_menu']}),
                 ('About it', {'fields': ['descrizione_menu', 'prezzo', 'cod_locale']}),
                 ]
    list_display = ['nome_menu', 'descrizione_menu', 'prezzo']
    list_select_related = [
        'cod_locale'
    ]
    inlines = [MenuInLine]


class TipoAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['nome_tipo']}), ]
    list_display = ['nome_tipo']


class ChiusuraAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['giorno_chiusura', 'cod_locale']}), ]
    list_display = ['cod_locale', 'giorno_chiusura']
    ordering = ['cod_locale']


class FotoLocaleAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['cod_locale', 'foto_locale']}), ]
    list_display = ['cod_locale', 'foto_locale']
    ordering = ['cod_locale']


class CompostoDaAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['cod_locale', 'nome_menu', 'nome_prodotto']})]
    list_display = ['cod_locale', 'nome_menu', 'nome_prodotto']
    ordering = ['cod_locale']


admin.site.register(Localita, LocalitaAdmin)
admin.site.register(Locale, LocaleAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Prodotto, ProdottoAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Tipo, TipoAdmin)
admin.site.register(Chiusura, ChiusuraAdmin)
admin.site.register(FotoLocale, FotoLocaleAdmin)
admin.site.register(CompostoDa, CompostoDaAdmin)
