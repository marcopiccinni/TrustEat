from django import forms


class EditRecUser(forms.Form):
    voto = forms.IntegerField(max_value=5, min_value=1, required=True)
    descrizione = forms.CharField(max_length=130, required=False)
