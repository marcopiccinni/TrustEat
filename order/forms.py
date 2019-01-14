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

        carte = Utente.carta_di_credito.through.objects.filter(
            utente_id=User.objects.get(username=LocalList.last_user).id)
        wanted_items = set()
        for carta in carte:
            c_id = carta.cartadicredito_id
            if CartaDiCredito.objects.get(cod_carta=c_id).is_valid():
                wanted_items.add(CartaDiCredito.objects.get(cod_carta=c_id).pk)

        self.fields['Carta'].queryset = CartaDiCredito.objects.filter(pk__in=wanted_items)
