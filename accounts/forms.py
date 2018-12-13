from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from TrustEat.maps import geocode
from .models import Utente, Commerciante, User
from user.models import CartaDiCredito
from localManagement.models import Localita, Tag, Locale, FotoLocale
from django.contrib.auth import get_user_model
import datetime
from django.contrib.auth import login
from django.shortcuts import render_to_response, redirect, HttpResponse


class RegUser(UserCreationForm):
    username = forms.CharField(required=True)
    nome = forms.CharField(required=True)
    cognome = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    cap = forms.ModelChoiceField(queryset=Localita.objects.all(), required=True, label="città")
    via = forms.CharField(required=True)
    civico = forms.CharField(required=True)
    telefono = forms.CharField(required=True)
    carta_di_credito = forms.CharField(max_length=16, required=False,
                                       help_text="Necessario per inserire una carta" +
                                                 "<br> Se lasciato vuoto la carta non sara' aggiunta"
                                       )
    intestatario = forms.CharField(max_length=100, required=False)
    scadenza = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'class': 'form-control',
               'type': 'date'}), help_text="Il giorno non verra' considerato", )

    class Meta:
        model = get_user_model()
        fields = ['username', 'nome', 'cognome', 'email', 'telefono', 'cap', 'via', 'civico', 'password1', 'password2']

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if User.objects.filter(telefono=telefono).exists():
            raise forms.ValidationError("Il telefono inserito esiste gia'")
        else:
            return telefono

    def clean_carta_di_credito(self):
        carta_di_credito = self.cleaned_data['carta_di_credito']
        if carta_di_credito is not "":
            raise forms.ValidationError("Inserire correttamente il numero della carta(16 cifre)")
        else:
            return carta_di_credito

    def clean_intestatario(self):
        intestatario = self.cleaned_data['intestatario']
        if self.cleaned_data['carta_di_credito'] is not "":
            if intestatario == "":
                raise forms.ValidationError("Inserire correttamente l'intestatario")
        else:
            return intestatario

    def clean_scadenza(self):
        scadenza = self.cleaned_data['scadenza']
        if self.cleaned_data['carta_di_credito'] is not "":
            raise forms.ValidationError("Inserire correttamente la scadenza")
        else:
            return scadenza

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome']
        user.last_name = self.cleaned_data['cognome']
        user.email = self.cleaned_data['email']
        user.via = self.cleaned_data['via']
        user.civico = self.cleaned_data['civico']
        user.cap = self.cleaned_data['cap'].cap
        user.telefono = self.cleaned_data['telefono']
        user.is_utente = True

        # ---------------- geocoding ------------------------------------
        user.latitude, user.longitude = geocode(
            str(user.via) + ',' + str(user.civico) + ',' + str(user.cap) + ',' + 'Italia')

        user.save()
        utente = Utente.objects.create(user=user)

        carta = self.cleaned_data['carta_di_credito']

        if carta is not "":
            CartaDiCredito.objects.create(numero_carta=self.cleaned_data['carta_di_credito'],
                                          intestatario=self.cleaned_data['intestatario'],
                                          scadenza=self.cleaned_data['scadenza'])

        if commit:
            utente.save()
        return user


class RegComm(UserCreationForm):
    username = forms.CharField(required=True)
    nome = forms.CharField(required=True)
    cognome = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    cap = forms.ModelChoiceField(queryset=Localita.objects.all(), required=True, label="città")
    via = forms.CharField(required=True)
    civico = forms.CharField(required=True)
    telefono = forms.CharField(required=True)
    p_iva = forms.CharField(required=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'nome', 'cognome', 'email', 'telefono', 'p_iva', 'cap', 'via', 'civico', 'password1',
                  'password2']

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if User.objects.filter(telefono=telefono).exists():
            raise forms.ValidationError("Il telefono inseirito esiste gia'")
        else:
            return telefono

    def clean_p_iva(self):
        p_iva = self.cleaned_data['p_iva']
        if Commerciante.objects.filter(p_iva=self.cleaned_data['p_iva']).exists():
            raise forms.ValidationError("La partita iva inserita esiste gia'")

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome']
        user.last_name = self.cleaned_data['cognome']
        user.email = self.cleaned_data['email']
        user.via = self.cleaned_data['via']
        user.civico = self.cleaned_data['civico']
        user.cap = self.cleaned_data['cap'].cap
        user.telefono = self.cleaned_data['telefono']
        user.is_commerciante = True

        # ---------------- geocoding ------------------------------------
        user.latitude, user.longitude = geocode(
            str(user.via) + ',' + str(user.civico) + ',' + str(user.cap) + ',' + 'Italia')

        user.save()
        commerciante = Commerciante.objects.create(user=user)
        commerciante.p_iva = self.cleaned_data['p_iva']

        if commit:
            commerciante.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class InsertLoginSocial(forms.Form):
    CHOICES = [('utente', 'utente'),
               ('commerciante', 'commerciante')]
    tipo_utente = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())

    cap = forms.ModelChoiceField(queryset=Localita.objects.all(), label='città')
    via = forms.CharField(widget=forms.TextInput())
    civico = forms.CharField(widget=forms.TextInput())
    telefono = forms.CharField(widget=forms.TextInput())

    carta_di_credito = forms.CharField(required=False, widget=forms.TextInput(
        attrs={
            'placeholder': 'Numero carta..es: 1111222233334444'
        }
    ), help_text="Inserire solamente se hai selezionato utente" +
                 "<br>Necessario per inserire una carta" +
                 "<br>Se lasciato vuoto la carta non sara' aggiunta")

    intestatario = forms.CharField(max_length=100, required=False)
    scadenza = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'class': 'form-control',
               'type': 'date'}), label="Scadenza (il giorno non verra' considerato)", )

    p_iva = forms.CharField(widget=forms.TextInput(), required=False,
                            help_text="Inserire solamente se hai selezionato commerciante")


class EditPersonalData(forms.Form):
    email = forms.EmailField()
    nome = forms.CharField(widget=forms.TextInput())
    cognome = forms.CharField(widget=forms.TextInput())
    password_attuale = forms.CharField(widget=forms.PasswordInput())
    nuova_password = forms.CharField(widget=forms.PasswordInput())
    conferma_password = forms.CharField(widget=forms.PasswordInput())
    cap = forms.ModelChoiceField(queryset=Localita.objects.all(), label='città')
    via = forms.CharField(widget=forms.TextInput())
    civico = forms.CharField(widget=forms.TextInput())
    telefono = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = get_user_model()
        field = ['email', 'nome', 'cognome', 'telefono', 'password_attuale', 'cap', 'via', 'civico', 'nuova_password',
                 'conferma_password']


class EditCommData(forms.Form):
    email = forms.EmailField()
    nome = forms.CharField(widget=forms.TextInput())
    cognome = forms.CharField(widget=forms.TextInput())
    password_attuale = forms.CharField(widget=forms.PasswordInput())
    nuova_password = forms.CharField(widget=forms.PasswordInput())
    conferma_password = forms.CharField(widget=forms.PasswordInput())
    cap = forms.ModelChoiceField(queryset=Localita.objects.all(), label='città')
    via = forms.CharField(widget=forms.TextInput())
    civico = forms.CharField(widget=forms.TextInput())
    telefono = forms.CharField(widget=forms.TextInput())
    p_iva = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = get_user_model()
        field = ['email', 'nome', 'cognome', 'telefono', 'cap', 'via', 'civico', 'p_iva', 'password_attuale',
                 'nuova_password', 'conferma_password']
