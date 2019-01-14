from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, View
from .models import OrdineInAttesa, RichiedeP, RichiedeM
from .forms import OrderForm, CardOrderForm
from localManagement.models import Locale, Localita, Prodotto, Menu
from localManagement.views import LocalList
from accounts.models import User, Utente, Commerciante
from user.models import CartaDiCredito
from TrustEat.settings import GOOGLE_MAPS_SECRET_API_KEY
from TrustEat.maps import distance_time
import datetime


class Check(CreateView):
    template_name = 'order/check.html'

    @classmethod
    def get(cls, request, *args):
        if request.user.is_anonymous or not request.user.is_utente:
            return redirect('/')

        destination = {"citta": Localita.objects.get(cap=User.objects.get(username=LocalList.last_user).cap),
                       "indirizzo": User.objects.get(username=LocalList.last_user).via,
                       "civico": User.objects.get(username=LocalList.last_user).civico,
                       "recapito": str(User.objects.get(username=LocalList.last_user).first_name) + " " + str(
                           User.objects.get(username=LocalList.last_user).last_name)}
        form = OrderForm()
        form_card = CardOrderForm()
        locale = Locale.objects.get(pk=int(LocalList.last_local))
        products = LocalList.prod_ordine
        menues = LocalList.menu_ordine
        num_prod = 0
        for x in products:
            num_prod += x['num_obj']
        num_menu = 0
        for x in menues:
            num_menu += x['num_obj']

        tmax = Locale.objects.get(pk=int(LocalList.last_local)).orario_chiusura
        if str(tmax) == '00:00:00':
            tmax = '23:59'

        tmin = Locale.objects.get(pk=int(LocalList.last_local)).orario_apertura
        if str(tmax) > str(datetime.datetime.now().strftime("%H:%M")) > str(tmin):
            tmin = datetime.datetime.now().strftime("%H:%M")

        context = {'products': products, 'num_prod': num_prod, 'menues': menues, 'num_menu': num_menu,
                   'locale': locale, 'destination': destination, 'tmin': tmin, 'tmax': tmax,
                   'form': form, 'form_card': form_card}
        return render(request, cls.template_name, context)

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
                        redirect('order:check')
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
        if request.user.is_anonymous or not request.user.is_utente:
            return redirect('/')

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

        dealers = [dealer.user.id for dealer in
                   Commerciante.objects.filter(possiede_locale__cod_locale=locale.cod_locale).all()]

        context = {
            'locale': locale, 'user': user, 'user_location': user_location,
            'ordine': ordine, 'prodotti': prodotti, 'menues': menues,
            'total': round(total + locale.prezzo_di_spedizione, 2), 'dealers': dealers}
        return render(request, cls.template_name, context)


class ReviewOrder(View):
    template_name = 'order/placed_order.html'

    @classmethod
    def get(cls, request, cod_ordine):
        if request.user.is_anonymous:
            return redirect('/')

        if RichiedeP.objects.filter(cod_ordine_id=cod_ordine).count():
            locale = RichiedeP.objects.filter(cod_ordine_id=cod_ordine).last().cod_locale
        elif RichiedeM.objects.filter(cod_ordine_id=cod_ordine).count():
            locale = RichiedeM.objects.filter(cod_ordine_id=cod_ordine).last().cod_locale
        else:
            return redirect('/')
        prodotti = []
        menues = []
        ordine = OrdineInAttesa.objects.get(cod_ordine=cod_ordine)
        utente = request.user
        dealers = [dealer.user.id for dealer in
                   Commerciante.objects.filter(possiede_locale__cod_locale=locale.cod_locale).all()]

        if utente.id == OrdineInAttesa.objects.get(cod_ordine=cod_ordine).email.user_id or utente.id in dealers:

            for p in ordine.prodotti.all():
                num_obj = RichiedeP.objects.get(cod_locale=locale, cod_ordine=ordine, nome_prodotto=p).quantita
                prodotti.append({'obj': p, 'num_obj': num_obj})

            for m in ordine.menues.all():
                num_obj = RichiedeM.objects.get(cod_locale=locale, cod_ordine=ordine, nome_menu=m).quantita
                menues.append({'obj': m, 'num_obj': num_obj})

            if utente.is_commerciante:
                utente = ordine.email.user

            user_location = Localita.objects.get(cap=User.objects.get(username=utente.username).cap).nome_localita
            context = {
                'locale': locale, 'user': utente, 'user_location': user_location, 'dealers': dealers,
                'ordine': ordine, 'prodotti': prodotti, 'menues': menues, 'total': total_price(cod_ordine),
            }
            return render(request, cls.template_name, context)
        return redirect('/')


class ListOrder(View):
    template_name = 'order/list_order.html'

    def get(self, request, cod_locale):
        if request.user.is_anonymous or not request.user.is_commerciante:
            return redirect('/')

        locale = get_object_or_404(Locale, pk=cod_locale)
        local = {'locale': locale, 'position': {'lat': locale.latitude, 'lon': locale.longitude}}
        if request.user.is_commerciante and request.user in \
                User.objects.filter(id__in=local['locale'].possiede_locale.all()):
            s = set()
            for x in RichiedeP.objects.filter(cod_locale=cod_locale).all():
                s.add(x.cod_ordine_id)
            for x in RichiedeM.objects.filter(cod_locale=cod_locale).all():
                s.add(x.cod_ordine_id)
            waiting_list = []
            refused_list = []
            tmp_delivering_list = []
            delivered_list = []
            delivering_js = []
            s = sorted(s, key=int)
            for x in s:
                ordine = OrdineInAttesa.objects.get(cod_ordine=x)
                print('Ordine: ', ordine.pk, ordine.accettato, ordine.consegnato)
                distance = 'None km'
                time = 'None mins'
                # -----------------------------------------------------------------------------------------------------
                # In caso sia possibile attivare il calcolo della distanza e tempo
                locale = Locale.objects.get(cod_locale=cod_locale)
                persona = ordine.email.user
                distance, time = distance_time(
                    origin=str(locale.via) + ',' + str(locale.num_civico) + ',' + str(locale.cap_id) + ',Italia',
                    arrival=str(persona.via) + ',' + str(persona.civico) + ',' + str(persona.cap) + ',Italia')
                # -----------------------------------------------------------------------------------------------------
                tmp = {'ordine': ordine, 'totale': total_price(ordine.cod_ordine),
                       'location': Localita.objects.get(cap=ordine.email.user.cap),
                       'distance': distance, 'time': time}
                tmp1 = {'ordine': ordine.cod_ordine,
                        'lat': ordine.email.user.latitude, 'lon': ordine.email.user.longitude}
                if ordine.accettato is None:
                    waiting_list.append(tmp)
                elif not ordine.accettato:
                    print('rifiutato: ', ordine.pk)
                    refused_list.append(tmp)
                elif ordine.accettato:
                    if ordine.consegnato:
                        delivered_list.append(tmp)
                    else:
                        tmp_delivering_list.append(tmp)
                        delivering_js.append(tmp1)

            # Ordinamento in base all'orario richiesto. non in ordine di codice
            delivering_list = []
            for x in tmp_delivering_list:
                if len(delivering_list):
                    ins = False
                    for elem in delivering_list:
                        if x['ordine'].orario_richiesto < elem['ordine'].orario_richiesto:
                            delivering_list.insert(delivering_list.index(elem), x)
                            ins = True
                            break
                    if not ins:
                        delivering_list.append(x)
                else:
                    delivering_list.append(x)
            print('delivering_list: ', delivering_list)
            print('delivering_js: ', delivering_js)

            args = {'waiting_list': waiting_list, 'refused_list': refused_list[::-1],
                    'delivering_list': delivering_list, 'delivering_js': delivering_js,
                    'delivered_list': delivered_list[::-1], 'local': local,
                    'googleKey': GOOGLE_MAPS_SECRET_API_KEY}
            return render(request, self.template_name, args)
        return redirect('/')

    def post(self, request, cod_locale):
        if request.POST:
            keys = request.POST.keys()
            if 'Consegnato' in keys:
                c = request.POST['Consegnato']
                OrdineInAttesa.objects.filter(cod_ordine=c).update(consegnato=True)
            elif 'Accettato' in keys:
                c = request.POST['Accettato']
                d = request.POST['Descrizione' + c]
                OrdineInAttesa.objects.filter(cod_ordine=c).update(accettato=True, descrizione=d)
            elif 'Rifiutato' in keys:
                c = request.POST['Rifiutato']
                d = request.POST['Descrizione' + c]
                OrdineInAttesa.objects.filter(cod_ordine=c).update(accettato=False, descrizione=d)

        return redirect('order:list_order', cod_locale)


def total_price(cod_ordine):
    locale = 0
    ordine = OrdineInAttesa.objects.get(cod_ordine=cod_ordine)
    if RichiedeP.objects.filter(cod_ordine_id=cod_ordine).count():
        locale = RichiedeP.objects.filter(cod_ordine_id=cod_ordine).last().cod_locale
    elif RichiedeM.objects.filter(cod_ordine_id=cod_ordine).count():
        locale = RichiedeM.objects.filter(cod_ordine_id=cod_ordine).last().cod_locale
    else:
        return locale

    total = float(locale.prezzo_di_spedizione)
    for p in ordine.prodotti.all():
        num_obj = RichiedeP.objects.get(cod_locale=locale, cod_ordine=ordine, nome_prodotto=p).quantita
        total += float(num_obj) * float(p.prezzo)
    for m in ordine.menues.all():
        num_obj = RichiedeM.objects.get(cod_locale=locale, cod_ordine=ordine, nome_menu=m).quantita
        total += float(num_obj) * float(m.prezzo)
    return round(total, 2)


def db_order_consistance():
    for not_accepted in OrdineInAttesa.objects.filter(accettato=None):
        if not_accepted.data.date() < datetime.datetime.now().date():
            OrdineInAttesa.objects.filter(pk=not_accepted.cod_ordine) \
                .update(accettato=False, descrizione='Ordine annullato. Il commerciante non ha risposto.')

    for accepted in OrdineInAttesa.objects.filter(accettato=True, consegnato__in=(None, False)):
        if accepted.data.date() < datetime.datetime.now().date():
            OrdineInAttesa.objects.filter(pk=accepted.cod_ordine) \
                .update(accettato=False,
                        descrizione='Consegna annullata. Contattare il locale per maggiori informazioni.')
    return
