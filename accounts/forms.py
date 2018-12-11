from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from TrustEat.maps import geocode
from .models import Utente, Commerciante, User
from localManagement.models import Localita, Tag, Locale, FotoLocale
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.shortcuts import render_to_response, redirect, HttpResponse


class RegUser(UserCreationForm):
    username = forms.CharField(required=True)
    nome = forms.CharField(required=True)
    cognome = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    via = forms.CharField(required=True)
    civico = forms.CharField(required=True)
    telefono = forms.CharField(required=True)
    cap = forms.ModelChoiceField(queryset=Localita.objects.all(), required=True)

    class Meta:
        model = get_user_model()
        fields = ["username", "nome", "cognome", "password1", "password2", "email", "via", "civico", "telefono", "cap"]

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

        if commit:
            utente.save()
        return user


class RegComm(UserCreationForm):
    username = forms.CharField(required=True)
    nome = forms.CharField(required=True)
    cognome = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    cap = forms.ModelChoiceField(queryset=Localita.objects.all(), required=True)
    via = forms.CharField(required=True)
    civico = forms.CharField(required=True)
    telefono = forms.CharField(required=True)
    p_iva = forms.CharField(required=True)

    class Meta:
        model = get_user_model()
        fields = ["username", "nome", "cognome", "password1", "password2", "email", "via", "civico", "telefono", "cap",
                  'p_iva']

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if User.objects.filter(telefono=telefono).exists():
            raise forms.ValidationError("Il telefono inseirito esiste gia'")
        else:
            return telefono

    @transaction.atomic
    def save(self, commit=True):
        url = 'Cliccare qui per tornare immediatamente alla home'
        user = super().save(commit=False)
        if User.objects.filter(telefono=self.cleaned_data['telefono']).exists():
            user.save()
            return user
            # raise forms.ValidationError('Il telefono inserito esiste gia. Tornare indetro ed inserirne uno corretto')
        elif Commerciante.objects.filter(p_iva=self.cleaned_data['p_iva']).exists():
            user.save()
            return user
        # raise forms.ValidationError("La p_iva inserita esiste gia'. Tornare indietro ed inserire una corretta")
        else:
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

    cap = forms.ModelChoiceField(queryset=Localita.objects.all())
    via = forms.CharField(widget=forms.TextInput())
    civico = forms.CharField(widget=forms.TextInput())
    telefono = forms.CharField(widget=forms.TextInput())

    # carta_di_credito = forms.CharField(required=False, widget=forms.TextInput(
    #     attrs={
    #         'placeholder': 'Numero carta..es: 1111222233334444'
    #     }
    # ))
    p_iva = forms.CharField(widget=forms.TextInput(), required=False)


class EditPersonalData(forms.Form):
    email = forms.EmailField()
    nome = forms.CharField(widget=forms.TextInput())
    cognome = forms.CharField(widget=forms.TextInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    cap = forms.ModelChoiceField(queryset=Localita.objects.all())
    via = forms.CharField(widget=forms.TextInput())
    civico = forms.CharField(widget=forms.TextInput())
    telefono = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = get_user_model()
        field = ['email', 'nome', 'cognome' 'password1', 'password2', 'cap', 'via', 'civico', 'telefono']


class EditCommData(forms.Form):
    email = forms.EmailField()
    nome = forms.CharField(widget=forms.TextInput())
    cognome = forms.CharField(widget=forms.TextInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    cap = forms.ModelChoiceField(queryset=Localita.objects.all())
    via = forms.CharField(widget=forms.TextInput())
    civico = forms.CharField(widget=forms.TextInput())
    telefono = forms.CharField(widget=forms.TextInput())
    p_iva = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = get_user_model()
        field = ['email', 'nome', 'cognome', 'password1', 'password2', 'cap', 'via', 'civico', 'telefono', 'p_iva']
