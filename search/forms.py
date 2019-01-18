from django import forms
from localManagement.models import Localita, Tag


class SearchForm(forms.Form):
    Position = forms.ModelChoiceField(queryset=Localita.objects.all().order_by('nome_localita'),
                                      label='Dove vuoi cercare?', required=False,
                                      )
    Tag = forms.ModelMultipleChoiceField(queryset=Tag.objects.order_by('nome_tag'),
                                         label='Vuoi cercare con più precisione?',
                                         help_text='Usa ctrl per la selezione multipla',
                                         required=False,
                                         )
    CercaNome= forms.CharField(label='Oppure... <br>cerca per nome:', required=False)