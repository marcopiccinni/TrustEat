from django.contrib.auth.forms import UserCreationForm
from django import forms
from localManagement.models import FotoLocale, Locale, Localita, Tag
from accounts.models import User, Utente
from user.models import CartaDiCredito
from localManagement.views import LocalList
from django.shortcuts import get_object_or_404, render


class OrderForm(forms.Form):
    Orario = forms.TimeField(input_formats=['%H:%M'], label="Inserisci l'orario in cui ricevere l'ordine")
    Pagamento = forms.ChoiceField(choices=[("True", "Carta di credito"), ("False", "Alla consegna")],
                                  required=True, initial="False", label='Come preferisci pagare?')


class CardOrderForm(forms.Form):
    Carta = forms.ModelChoiceField(required=False, queryset=CartaDiCredito.objects.all(), disabled=True)

    def __init__(self, *args, **kwargs):
        super(CardOrderForm, self).__init__(*args, **kwargs)
        self.fields['Carta'].queryset = Utente.objects.get(
            pk=User.objects.get(username=LocalList.last_user).pk).cartadicredito_set.all()
