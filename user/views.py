from django.views.generic import View
from .models import CartaDiCredito
from accounts.models import Utente
from django.shortcuts import render, redirect, HttpResponseRedirect
from .forms import AddCreditCardForm
from datetime import date

class AddCreditCard(View):
    form = AddCreditCardForm()
    template_name = 'user/add_cc.html'
    form_class = AddCreditCardForm

    def get(self, request):
        if request.user.is_anonymous or not request.user.is_utente :
            return redirect('/')

        form = AddCreditCardForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.method == 'POST':
            form = AddCreditCardForm(request.POST or None)
            if form.is_valid():
                carta_di_credito = form.cleaned_data['carta_di_credito']
                intestatario = form.cleaned_data['intestatario']
                scadenza = form.cleaned_data['scadenza']
                current_user = request.user

                if carta_di_credito is not "":
                    if intestatario is "":
                        messaggio = 'ERRORE'
                        messaggio1 = 'Carta non aggiunta. Intestatario mancante'
                        url = "Clicca qui per tornare all'area utente"
                        context = {'messaggio': messaggio, 'messaggio1': messaggio1, 'url': url}
                        return render(request, 'user/successo_insuccesso_carta.html', context)
                    elif scadenza is None:
                        messaggio = 'ERRORE'
                        messaggio1 = 'Carta non aggiunta. Scadenza mancante'
                        url = "Clicca qui per tornare all'area utente"
                        context = {'messaggio': messaggio, 'messaggio1': messaggio1, 'url': url}
                        return render(request, 'user/successo_insuccesso_carta.html', context)
                    else:
                        if scadenza is not None:

                            c = CartaDiCredito(numero_carta=carta_di_credito, intestatario=intestatario,
                                               scadenza=scadenza)
                            if not c.is_valid():
                                messaggio = 'ERRORE'
                                messaggio1 = 'Carta scaduta'
                                url = "Clicca qui per tornare all'area utente"
                                context = {'messaggio': messaggio, 'messaggio1': messaggio1, 'url': url}
                                return render(request, 'user/successo_insuccesso_carta.html', context)
                            else:
                                c.save()
                                u = Utente.objects.get(user=current_user)
                                u.carta_di_credito.add(CartaDiCredito.objects.get(numero_carta=carta_di_credito).pk)

                                messaggio = 'Successo'
                                messaggio1 = 'Aggiunta della carta avvenuta con successo'
                                url = "Clicca qui per tornare all'area utente"
                                context = {'messaggio': messaggio, 'messaggio1': messaggio1, 'url': url}
                                return render(request, 'user/successo_insuccesso_carta.html', context)
                else:
                    messaggio = 'Insuccesso'
                    messaggio1 = 'Carta non aggiunta. Compilare il form correttamente e riprovare'
                    url = "Clicca qui per tornare all'area utente"
                    context = {'messaggio': messaggio, 'messaggio1': messaggio1, 'url': url}
                    return render(request, 'user/successo_insuccesso_carta.html', context)


class DeleteCard(View):
    @staticmethod
    def get(request, cod_carta):
        if request.user.is_anonymous or not request.user.is_utente:
            return redirect('/')

        if CartaDiCredito.objects.filter(cod_carta=cod_carta).exists():
            messaggio = "Successo"
            messaggio1 = "l'eliminazione della carta di credito e' avvenuta con successo"
            url = "Clicca qui se invece vuoi tornare all'area utente"
            Utente.carta_di_credito.through.objects.filter(cartadicredito_id=cod_carta).delete()
            CartaDiCredito.objects.filter(cod_carta=cod_carta).delete()
            data = {'messaggio': messaggio, 'messaggio1': messaggio1, 'url': url}
            return render(request, 'user/successo_insuccesso_carta.html', data)
        else:
            messaggio = "Errore"
            messaggio1 = "Qualcosa e' andato storto, controllare che il prodotto esista e riprovare"
            url = "Clicca qui per tornare alla pagina dei menu"
            context = {'messaggio': messaggio, 'messaggio1': messaggio1, 'url': url}
            return render(request, 'user/successo_insuccesso_carta.html', context)
