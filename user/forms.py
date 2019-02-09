from django import forms
from .models import CartaDiCredito


class EditRecUser(forms.Form):
    voto = forms.IntegerField(max_value=5, min_value=1, required=True)
    descrizione = forms.CharField(max_length=130, required=False)


class AddCreditCardForm(forms.Form):
    carta_di_credito = forms.CharField(max_length=16, required=False,
                                       help_text="Necessario per inserire una carta" +
                                                 "<br> Se lasciato vuoto la carta non sara' aggiunta"
                                       )
    intestatario = forms.CharField(max_length=100, required=False)
    scadenza = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'class': 'form-control',
               'type': 'date'}), help_text="Il giorno non verra' considerato", )

    class Meta:
        model = CartaDiCredito()
        fields = '__all__'
