from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import FotoLocale, Locale, Localita, Tag, Prodotto, Tipo, Menu
from accounts.models import Commerciante
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render


class QuantityForm(forms.Form):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput(), min_value=0)
    num_object = forms.IntegerField(min_value=0, max_value=99, widget=forms.NumberInput(), initial=0, label='')
    isProduct = forms.BooleanField(required=False, widget=forms.HiddenInput(), initial=False)


class ReviewForm(forms.Form):
    Voto = forms.IntegerField(required=True, min_value=1, max_value=5, label='Voto', widget=forms.NumberInput(
        attrs={'style': 'width: 60px',
               'class': 'mx-5 my-0',
               }
    ))
    Descrizione = forms.CharField(required=False, label='Recensione', widget=forms.TextInput(
        attrs={'placeholder': 'Aggiungi qui un commento',
               'class': 'ml-2 my-0',
               'style': 'width: 900px',
               }
    ))


class ReplayForm(forms.Form):
    # Username = forms.ModelChoiceField(queryset=Recensione.objects.all(), required=True,
    #                                   label="Seleziona l'utente a cui rispondere",
    #                                   widget=forms.Select(
    #                                       attrs={'class': 'ml-2 mb-1',
    #                                              }))
    Username = forms.ChoiceField(required=True, label="Seleziona l'utente a cui rispondere",
                                 widget=forms.Select(attrs={
                                     'class': 'ml-2 my-0',
                                 }))
    Descrizione = forms.CharField(required=True, label='Risposta', widget=forms.TextInput(
        attrs={'placeholder': 'Aggiungi qui la risposta',
               'class': 'ml-2 my-0',
               'style': 'width: 100px',
               }
    ))


class CreateLocalForm(forms.Form):
    nome_locale = forms.CharField(max_length=30, required=True, widget=forms.TextInput())
    orario_apertura = forms.TimeField(required=True, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'ore:minuti',
            'class': 'text-center'
        }
    ))
    orario_chiusura = forms.TimeField(required=True, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'ore:minuti',
            'class': 'text-center'
        }))
    cap = forms.ModelChoiceField(queryset=Localita.objects.all(), required=True)
    via = forms.CharField(max_length=50, widget=forms.TextInput(), required=True)
    num_civico = forms.CharField(max_length=10, widget=forms.TextInput(), required=True)
    descrizione = forms.CharField(max_length=200, widget=forms.TextInput(), required=True)
    telefono = forms.CharField(max_length=15, widget=forms.TextInput(), required=True)
    sito_web = forms.CharField(max_length=50, widget=forms.TextInput(), required=True)
    email = forms.EmailField(required=True, widget=forms.TextInput(
        attrs={
            'ass': 'form-control',
            'placeholder': 'example@example.com',
            'class': 'text-center'
        }))
    prezzo_di_spedizione = forms.FloatField(required=True)
    tag = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(),
                                         widget=forms.CheckboxSelectMultiple,
                                         required=True
                                         )

    CHOICES = [
        ('Lunedì', 'Lunedì'),
        ('Martedì', 'Martedì'),
        ('Mercoledì', 'Mercoledì'),
        ('Giovedì', 'Giovedì'),
        ('Venerdì', 'Venerdì'),
        ('Sabato', 'Sabato'),
        ('Domenica', 'Domenica'),
    ]

    giorno_chiusura = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    altri_proprietari = forms.ModelMultipleChoiceField(queryset=Commerciante.objects.all(),
                                                       required=False)

    foto_locale1 = forms.ImageField(required=True)
    foto_locale2 = forms.ImageField(required=False)
    foto_locale3 = forms.ImageField(required=False)

    class Meta:
        model = Locale, FotoLocale
        fields = ['nome_locale', 'orario_apertura', 'orario_chiusura', 'cap', 'via', 'numero_civico', 'descrizione',
                  'telefono', 'sito_web', 'email', 'prezzo_di_spedizione', 'tag', 'carta_di_credito', 'giorno_chiusura',
                  'altri_proprietari', 'foto_locale1', 'foto_locale2', 'foto_locale3']


class EditLocal(forms.Form):
    nome_locale = forms.CharField(max_length=30, required=False, widget=forms.TextInput())
    orario_apertura = forms.TimeField(required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'ore:minuti',
        }
    ))
    orario_chiusura = forms.TimeField(required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'ore:minuti'
        }))
    cap = forms.ModelChoiceField(queryset=Localita.objects.all(), required=False)
    via = forms.CharField(max_length=50, widget=forms.TextInput(), required=False)
    num_civico = forms.CharField(max_length=10, widget=forms.TextInput(), required=False)
    descrizione = forms.CharField(max_length=200, widget=forms.TextInput(), required=False)
    telefono = forms.CharField(max_length=15, widget=forms.TextInput(), required=False)
    sito_web = forms.CharField(max_length=50, widget=forms.TextInput(), required=False)
    email = forms.EmailField(required=False, widget=forms.TextInput(
        attrs={
            'ass': 'form-control',
            'placeholder': 'example@example.com'
        }))
    prezzo_di_spedizione = forms.FloatField(required=False)

    tag = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False,
                                         widget=forms.CheckboxSelectMultiple)

    CHOICES = [
        ('Lunedì', 'Lunedì'),
        ('Martedì', 'Martedì'),
        ('Mercoledì', 'Mercoledì'),
        ('Giovedì', 'Giovedì'),
        ('Venerdì', 'Venerdì'),
        ('Sabato', 'Sabato'),
        ('Domenica', 'Domenica'),
    ]

    giorno_chiusura = forms.MultipleChoiceField(choices=CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    altri_proprietari = forms.ModelMultipleChoiceField(queryset=Commerciante.objects.all(), required=False)
    foto_locale1 = forms.ImageField(required=False)
    foto_locale2 = forms.ImageField(required=False)
    foto_locale3 = forms.ImageField(required=False)

    class Meta:
        model = Locale, FotoLocale
        fields = ['nome_locale', 'orario_apertura', 'orario_chiusura', 'cap', 'via', 'numero_civico', 'descrizione',
                  'telefono', 'sito_web', 'email', 'prezzo_di_spedizione', 'tag', 'giorno_chiusura',
                  'altri_proprietari', 'foto_locale1', 'foto_locale2',
                  'foto_locale3']


class EditProduct(forms.Form):
    nome_prodotto = forms.CharField(max_length=100, required=False, widget=forms.TextInput())
    descrizione_prodotto = forms.CharField(max_length=100, required=False, widget=forms.TextInput())
    prezzo = forms.FloatField(min_value=0, required=False)
    foto_prodotto = forms.ImageField(required=False)
    nome_tipo = forms.ModelChoiceField(queryset=Tipo.objects.all(), required=False)

    class Meta:
        model = Prodotto
        fields = ['nome_prodotto', 'descrizione_prodotto', 'prezzo', 'foto_prodotto', 'nome_tipo']


class AddEProduct(forms.Form):
    nome_prodotto = forms.CharField(max_length=100, required=True, widget=forms.TextInput())
    descrizione_prodotto = forms.CharField(max_length=100, required=True, widget=forms.TextInput())
    prezzo = forms.FloatField(min_value=0, required=True)
    foto_prodotto = forms.ImageField(required=True)
    nome_tipo = forms.ModelChoiceField(queryset=Tipo.objects.all(), required=True)

    class Meta:
        model = Prodotto
        fields = ['nome_prodotto', 'descrizione_prodotto', 'prezzo', 'foto_prodotto', 'nome_tipo']


class AddEMenu(forms.Form):
    nome_menu = forms.CharField(max_length=100, required=True, widget=forms.TextInput())
    descrizione_menu = forms.CharField(max_length=100, required=True, widget=forms.TextInput())
    prezzo = forms.FloatField(min_value=0, required=True)
    composto_da_prodotti = forms.ModelMultipleChoiceField(queryset=Prodotto.objects.all(),
                                                          widget=forms.CheckboxSelectMultiple(), required=True)

    class Meta:
        model = Menu
        fields = ['nome_menu', 'descrizione_menu', 'prezzo']


class ModMenu(forms.Form):
    nome_menu = forms.CharField(max_length=100, required=True, widget=forms.TextInput())
    descrizione_menu = forms.CharField(max_length=100, required=True, widget=forms.TextInput())
    prezzo = forms.FloatField(min_value=0, required=True)
    composto_da_prodotti = forms.ModelMultipleChoiceField(queryset=Prodotto.objects.all(),
                                                          widget=forms.CheckboxSelectMultiple(), required=False)

    class Meta:
        model = Menu
        fields = ['nome_menu', 'descrizione_menu', 'prezzo']
