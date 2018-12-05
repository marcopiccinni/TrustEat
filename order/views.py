from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import CreateView, View
from localManagement.models import Locale, Localita, Prodotto, Menu
from accounts.models import User, Utente
from user.models import CartaDiCredito
from .models import OrdineInAttesa, RichiedeP, RichiedeM
from localManagement.views import LocalList
from .forms import OrderForm, CardOrderForm
import datetime


def check(request):
    if not int(LocalList.last_local):
        return redirect('search:index')

    if request.method == 'POST':
        form = OrderForm(request.POST or None)
        if form.is_valid():
            orario = form.cleaned_data['Orario']
            pagamento = form.cleaned_data['Pagamento']
            carta = None
            if pagamento == 'True':
                carta = CartaDiCredito.objects.get(pk=form.data['Carta'])

    destination = {"citta": Localita.objects.get(cap=User.objects.get(username=LocalList.last_user).cap),
                   "indirizzo": User.objects.get(username=LocalList.last_user).via,
                   "civico": User.objects.get(username=LocalList.last_user).civico,
                   "recapito": str(User.objects.get(username=LocalList.last_user).first_name) + " " + str(
                       User.objects.get(username=LocalList.last_user).last_name),
                   }

    form = OrderForm()
    formCard = CardOrderForm()
    # formCard['Carta'].disabled = False
    locale = Locale.objects.get(pk=int(LocalList.last_local))
    template_name = 'order/check.html'
    products = LocalList.prod_ordine
    menues = LocalList.menu_ordine
    num_prod = 0
    for x in products:
        num_prod += x['num_obj']
    num_menu = 0
    for x in menues:
        num_menu += x['num_obj']

    tmin = Locale.objects.get(pk=int(LocalList.last_local)).orario_apertura
    if str(tmin) < str(datetime.datetime.now().strftime("%H:%M")):
        tmin = datetime.datetime.now().strftime("%H:%M")

    tmax = Locale.objects.get(pk=int(LocalList.last_local)).orario_chiusura
    if str(tmax) == '00:00:00':
        tmax = '23:59'

        context = {'products': products, 'menues': menues,
                   'num_prod': num_prod, 'num_menu': num_menu,
                   'locale': locale, 'destination': destination,
                   'tmin': tmin, 'tmax': tmax,
                   'form': form, 'form_card': formCard,
                   }
        return render(request, template_name, context)
    return redirect('search:index')


class Check(CreateView):
    template_name = 'order/check.html'

    @classmethod
    def get(cls, request, *args):
        destination = {"citta": Localita.objects.get(cap=User.objects.get(username=LocalList.last_user).cap),
                       "indirizzo": User.objects.get(username=LocalList.last_user).via,
                       "civico": User.objects.get(username=LocalList.last_user).civico,
                       "recapito": str(User.objects.get(username=LocalList.last_user).first_name) + " " + str(
                           User.objects.get(username=LocalList.last_user).last_name),
                       }

        form = OrderForm()
        form_card = CardOrderForm()
        # formCard['Carta'].disabled = False
        locale = Locale.objects.get(pk=int(LocalList.last_local))
        products = LocalList.prod_ordine
        menues = LocalList.menu_ordine
        num_prod = 0
        for x in products:
            num_prod += x['num_obj']
        num_menu = 0
        for x in menues:
            num_menu += x['num_obj']

        tmin = Locale.objects.get(pk=int(LocalList.last_local)).orario_apertura
        if str(tmin) < str(datetime.datetime.now().strftime("%H:%M")):
            tmin = datetime.datetime.now().strftime("%H:%M")

        tmax = Locale.objects.get(pk=int(LocalList.last_local)).orario_chiusura
        if str(tmax) == '00:00:00':
            tmax = '23:59'

            context = {'products': products, 'menues': menues,
                       'num_prod': num_prod, 'num_menu': num_menu,
                       'locale': locale, 'destination': destination,
                       'tmin': tmin, 'tmax': tmax,
                       'form': form, 'form_card': form_card,
                       }
            return render(request, cls.template_name, context)
        return redirect('search:index')

    @classmethod
    def post(cls, request, *args):
        if request.method == 'POST':
            form = OrderForm(request.POST or None)
            if form.is_valid():
                orario = form.cleaned_data['Orario']
                pagamento = form.cleaned_data['Pagamento']
                ordine = None
                if pagamento == 'True':
                    if form.data['Carta'] == '':
                        raise ValidationError('')
                    else:
                        ordine = OrdineInAttesa.objects.create(
                            email=Utente.objects.get(pk=User.objects.get(username=LocalList.last_user)),
                            data=datetime.datetime.now(), orario_richiesto=orario,
                            metodo_pagamento=OrdineInAttesa.CARD,
                            cod_carta=CartaDiCredito.objects.get(
                                pk=form.data['Carta']))
                else:
                    ordine = OrdineInAttesa.objects.create(
                        email=Utente.objects.get(pk=User.objects.get(username=LocalList.last_user)),
                        data=datetime.datetime.now(), orario_richiesto=orario,
                        metodo_pagamento=OrdineInAttesa.CASH)

                for prodotto in LocalList.prod_ordine:
                    if prodotto['num_obj'] > 0:
                        RichiedeP.objects.create(cod_ordine=ordine,
                                                 cod_locale=Locale.objects.get(pk=LocalList.last_local),
                                                 nome_prodotto=prodotto['prodotto'], quantita=prodotto['num_obj'])
                for menu in LocalList.menu_ordine:
                    if menu['num_obj'] > 0:
                        if menu['num_obj'] > 0:
                            RichiedeM.objects.create(cod_ordine=ordine,
                                                     cod_locale=Locale.objects.get(pk=LocalList.last_local),
                                                     nome_menu=menu['menu'], quantita=menu['num_obj'])
        return redirect('order:placed_order')


class PlacedOrder(View):
    template_name = 'order/placed_order.html'

    @classmethod
    def get(cls, request):
        locale = Locale.objects.get(pk=LocalList.last_local)
        user = User.objects.get(username=LocalList.last_user)
        user_location = Localita.objects.get(cap=user.cap).nome_localita
        ordine = OrdineInAttesa.objects.filter(email=Utente.objects.get(pk=user)).last()
        prodotti = []
        menues = []

        total = 0.0
        for p in ordine.prodotti.all():
            num_obj = RichiedeP.objects.get(cod_locale=locale, cod_ordine=ordine, nome_prodotto=p).quantita
            prodotti.append({'obj': p, 'num_obj': num_obj})
            total += float(num_obj) * float(p.prezzo)

        for m in ordine.menues.all():
            num_obj = RichiedeM.objects.get(cod_locale=locale, cod_ordine=ordine, nome_menu=m).quantita
            menues.append({'obj': m, 'num_obj': num_obj})
            total += float(num_obj) * float(m.prezzo)

        context = {
            'locale': locale, 'user': user, 'user_location': user_location,
            'ordine': ordine, 'prodotti': prodotti, 'menues': menues, 'total': total,
        }

        return render(request, cls.template_name, context)


class ReviewOrder(View):
    template_name = 'order/placed_order.html'

    @classmethod
    def get(cls, request, cod_ordine):
        if not request.user.id == OrdineInAttesa.objects.get(cod_ordine=cod_ordine).email.user_id:
            return redirect('/')
        if RichiedeP.objects.filter(cod_ordine_id=cod_ordine).count() \
                and request.user.id == OrdineInAttesa.objects.get(cod_ordine=cod_ordine).email.user_id:
            locale = RichiedeP.objects.filter(cod_ordine_id=cod_ordine).last().cod_locale
            print(locale)
            user_location = Localita.objects.get(cap=User.objects.get(username=request.user.username).cap).nome_localita
            ordine = OrdineInAttesa.objects.get(cod_ordine=cod_ordine)
            prodotti = []
            menues = []

            total = 0.0
            for p in ordine.prodotti.all():
                num_obj = RichiedeP.objects.get(cod_locale=locale, cod_ordine=ordine, nome_prodotto=p).quantita
                prodotti.append({'obj': p, 'num_obj': num_obj})
                total += float(num_obj) * float(p.prezzo)

            for m in ordine.menues.all():
                num_obj = RichiedeM.objects.get(cod_locale=locale, cod_ordine=ordine, nome_menu=m).quantita
                menues.append({'obj': m, 'num_obj': num_obj})
                total += float(num_obj) * float(m.prezzo)

            context = {
                'locale': locale, 'user': request.user, 'user_location': user_location,
                'ordine': ordine, 'prodotti': prodotti, 'menues': menues, 'total': total,
            }
            return render(request, cls.template_name, context)
        return redirect('/')


def db_order_consistance():
    for order in OrdineInAttesa.objects.filter(accettato=None):
        if order.data.date() < datetime.datetime.now().date():
            OrdineInAttesa.objects.filter(pk=order.cod_ordine).update(accettato=False,
                                                                      descrizione='Ordine annullato. '
                                                                                  'Il commerciante non ha risposto.')
    return
