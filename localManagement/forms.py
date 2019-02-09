from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import FotoLocale, Locale, Localita, Tag, Prodotto, Menu
from accounts.models import Commerciante
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render

DAY_CHOICES = [
    ('Lunedì', 'Lunedì'),
    ('Martedì', 'Martedì'),
    ('Mercoledì', 'Mercoledì'),
    ('Giovedì', 'Giovedì'),
    ('Venerdì', 'Venerdì'),
    ('Sabato', 'Sabato'),
    ('Domenica', 'Domenica'),
]


class QuantityForm(forms.Form):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput(), min_value=0)
    num_object = forms.IntegerField(min_value=0, max_value=99, widget=forms.NumberInput(), initial=0, label='')
    isProduct = forms.BooleanField(required=False, widget=forms.HiddenInput(), initial=False)


class ReviewForm(forms.Form):
    Voto = forms.IntegerField(required=True, min_value=1, max_value=5, label='Voto', widget=forms.NumberInput(
        attrs={'style': 'width: 60px', 'class': 'mx-5 my-0', }
    ))
    Descrizione = forms.CharField(required=False, label='Recensione', widget=forms.TextInput(
        attrs={'placeholder': 'Aggiungi qui un commento', 'class': 'ml-2 my-0', 'style': 'width: 100%', }
    ))


class ReplayForm(forms.Form):
    Username = forms.ChoiceField(required=True, label="Seleziona l'utente a cui rispondere",
                                 widget=forms.Select(attrs={'class': 'ml-2 my-0', })
                                 )
    Descrizione = forms.CharField(required=True, label='Risposta', widget=forms.TextInput(
        attrs={'placeholder': 'Aggiungi qui la risposta', 'class': 'ml-2 my-0', 'style': 'width: 100%', }
    ))


class CreateLocalForm(forms.Form):
    nome_locale = forms.CharField(max_length=30, required=True, widget=forms.TextInput(), label='Nome')
    orario_apertura = forms.TimeField(required=True, label='Orario di apertura', widget=forms.TextInput(
        attrs={'class': 'form-control text-center', 'placeholder': 'ore:minuti', }
    ))
    orario_chiusura = forms.TimeField(required=True, label='Orario di chiusura', widget=forms.TextInput(
        attrs={'class': 'form-control text-center', 'placeholder': 'ore:minuti', })
                                      )
    cap = forms.ModelChoiceField(queryset=Localita.objects.all(), required=True, label='Città')
    via = forms.CharField(max_length=50, widget=forms.TextInput(), required=True, label='Indirizzo')
    num_civico = forms.CharField(max_length=10, widget=forms.TextInput(), required=True)
    descrizione = forms.CharField(max_length=200, widget=forms.TextInput(), required=True)
    telefono = forms.CharField(max_length=15, widget=forms.TextInput(), required=True)
    sito_web = forms.CharField(max_length=50, widget=forms.TextInput(), required=False)
    email = forms.EmailField(required=False, widget=forms.TextInput(
        attrs={'ass': 'form-control', 'placeholder': 'example@example.com', 'class': 'text-center'})
                             )
    prezzo_di_spedizione = forms.FloatField(required=True)
    tag = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple, required=True)
    giorno_chiusura = forms.MultipleChoiceField(choices=DAY_CHOICES, widget=forms.CheckboxSelectMultiple,
                                                required=False, label='Giorno di chiusura')
    altri_proprietari = forms.ModelMultipleChoiceField(queryset=Commerciante.objects.all(), required=False)
    foto_locale1 = forms.ImageField(required=True)
    foto_locale2 = forms.ImageField(required=False)
    foto_locale3 = forms.ImageField(required=False)

    class Meta:
        model = Locale, FotoLocale
        fields = ['nome_locale', 'cap', 'via', 'numero_civico', 'telefono', 'sito_web', 'email', 'descrizione',
                  'prezzo_di_spedizione', 'tag', 'orario_apertura', 'orario_chiusura', 'giorno_chiusura',
                  'altri_proprietari', 'foto_locale1', 'foto_locale2', 'foto_locale3']


class EditLocal(forms.Form):
    nome_locale = forms.CharField(max_length=30, required=False, widget=forms.TextInput(), label='Nome')
    orario_apertura = forms.TimeField(required=False, label='Orario di apertura', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'ore:minuti', }
    ))
    orario_chiusura = forms.TimeField(required=False, label='Orario di chiusura', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'ore:minuti'}
    ))
    cap = forms.ModelChoiceField(queryset=Localita.objects.all(), required=False, label='Città')
    via = forms.CharField(max_length=50, widget=forms.TextInput(), required=False, label='Indirizzo')
    num_civico = forms.CharField(max_length=10, widget=forms.TextInput(), required=False)
    descrizione = forms.CharField(max_length=200, widget=forms.TextInput(), required=False)
    telefono = forms.CharField(max_length=15, widget=forms.TextInput(), required=False)
    sito_web = forms.CharField(max_length=50, widget=forms.TextInput(), required=False)
    email = forms.EmailField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'example@example.com'}
    ))
    prezzo_di_spedizione = forms.FloatField(required=False)
    tag = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False,
                                         widget=forms.CheckboxSelectMultiple)
    giorno_chiusura = forms.MultipleChoiceField(choices=DAY_CHOICES, required=False, label='Giorno di chiusura',
                                                widget=forms.CheckboxSelectMultiple)
    altri_proprietari = forms.ModelMultipleChoiceField(queryset=Commerciante.objects.all(), required=False)
    rimuovi_altri_proprietari = forms.BooleanField(required=False, label='Rimuovi altri proprietari')

    foto_locale1 = forms.ImageField(required=False)
    foto_locale2 = forms.ImageField(required=False)
    foto_locale3 = forms.ImageField(required=False)

    class Meta:
        model = Locale, FotoLocale
        fields = ['nome_locale', 'cap', 'via', 'numero_civico', 'telefono', 'sito_web', 'email', 'descrizione',
                  'prezzo_di_spedizione', 'tag', 'orario_apertura', 'orario_chiusura', 'giorno_chiusura',
                  'altri_proprietari', 'rimuovi_altri_proprietari', 'foto_locale1', 'foto_locale2', 'foto_locale3']


class EditProduct(forms.Form):
    nome_prodotto = forms.CharField(max_length=100, required=False, widget=forms.TextInput(), label='Nome')
    descrizione_prodotto = forms.CharField(max_length=100, required=False, widget=forms.TextInput(),
                                           label='Ingredienti')
    prezzo = forms.FloatField(min_value=0, required=False, max_value=99)
    foto_prodotto = forms.ImageField(required=False, label='Foto')

    class Meta:
        model = Prodotto
        fields = ['nome_prodotto', 'descrizione_prodotto', 'prezzo', 'foto_prodotto']


class AddEProduct(forms.Form):
    nome_prodotto = forms.CharField(max_length=100, required=True, widget=forms.TextInput(), label='Nome')
    descrizione_prodotto = forms.CharField(max_length=100, required=True, widget=forms.TextInput(), label='Ingredienti')
    prezzo = forms.FloatField(min_value=0, required=True, max_value=99)
    foto_prodotto = forms.ImageField(required=False)

    class Meta:
        model = Prodotto
        fields = ['nome_prodotto', 'descrizione_prodotto', 'prezzo', 'foto_prodotto']


class AddEMenu(forms.Form):
    nome_menu = forms.CharField(max_length=100, required=True, widget=forms.TextInput(), label='Nome')
    descrizione_menu = forms.CharField(max_length=100, required=True, widget=forms.TextInput(), label='Descrizione')
    prezzo = forms.FloatField(min_value=0, required=True, max_value=99)
    composto_da_prodotti = forms.ModelMultipleChoiceField(queryset=Prodotto.objects.all(), required=True,
                                                          widget=forms.CheckboxSelectMultiple(),
                                                          label='Prodotti inclusi')

    class Meta:
        model = Menu
        fields = ['nome_menu', 'descrizione_menu', 'prezzo']


class ModMenu(forms.Form):
    nome_menu = forms.CharField(max_length=100, required=True, widget=forms.TextInput(), label='Nome')
    descrizione_menu = forms.CharField(max_length=100, required=True, widget=forms.TextInput(), label='Descrizione')
    prezzo = forms.FloatField(min_value=0, required=True, max_value=99)
    composto_da_prodotti = forms.ModelMultipleChoiceField(queryset=Prodotto.objects.all(), required=False,
                                                          widget=forms.CheckboxSelectMultiple(),
                                                          label='Prodotti inclusi')

    class Meta:
        model = Menu
        fields = ['nome_menu', 'descrizione_menu', 'prezzo']
