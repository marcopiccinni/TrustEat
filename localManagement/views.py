from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from django.views.generic import UpdateView, TemplateView, CreateView, DeleteView, View
from .models import Tag, FotoLocale, Chiusura, Menu, Prodotto, CompostoDa, Localita, Locale
from .forms import ReplayForm, ReviewForm, AddEMenu, AddEProduct, CreateLocalForm, QuantityForm, ModMenu, \
    EditProduct, EditLocal
from accounts.models import Commerciante, User, Utente
from user.models import Recensione
from order.models import RichiedeM, RichiedeP, OrdineInAttesa
from TrustEat.maps import geocode
import datetime


class LocalList(View):
    form = QuantityForm()
    last_user = '0'
    last_local = '0'
    model = Localita
    form_class = QuantityForm
    template_name = 'localManagement/localLists.html'
    prod_ordine = []
    menu_ordine = []
    prod_list = []
    menu_list = []

    @staticmethod
    def init_obj(self, cod_locale):
        for x in Prodotto.objects.filter(cod_locale=cod_locale).all():
            self.prod_ordine.append({'id': x.id, 'num_obj': 0, 'prodotto': x})

        for x in Menu.objects.filter(cod_locale=cod_locale).all():
            self.menu_ordine.append({'id': x.id, 'num_obj': 0, 'menu': x})
        return

    @staticmethod
    def local_lists(self, cod_locale):
        local = get_object_or_404(Locale, pk=cod_locale)
        location = Localita.objects.get(cap=local.cap_id)
        photos = FotoLocale.objects.filter(cod_locale=cod_locale)
        count_vote = Recensione.objects.filter(cod_locale=cod_locale, voto__in=range(6)).count()
        avg_vote = 0
        if count_vote > 0:
            for v in Recensione.objects.filter(cod_locale=cod_locale, voto__in=range(6)):
                avg_vote += v.voto
            avg_vote /= count_vote

        photo_list = []
        num = photos.__len__() * 2
        pos = 0
        for pic in photos:
            photo_list.append({'pic': pic, 'pos': pos, 'min': (num - 1) * 111, 'max': (num + 1) * 111, })
            num -= 1
            pos += 1

        pos = 0
        self.prod_list = []
        for x in Prodotto.objects.filter(cod_locale=cod_locale).all().order_by("nome_prodotto"):
            form = None
            for l in self.prod_ordine:
                if l['id'] == x.id:
                    form = QuantityForm(initial={'id': x.id, 'num_object': l['num_obj'], 'isProduct': True})
                    break
            self.prod_list.append({'product': x, 'pos': pos, 'form': form})
            pos += 1

        pos = 0
        self.menu_list = []
        for x in Menu.objects.filter(cod_locale=cod_locale).all().order_by("nome_menu"):
            form = None
            for l in self.menu_ordine:
                if l['id'] == x.id:
                    form = QuantityForm(initial={'id': x.id, 'num_object': l['num_obj'], 'isProduct': False})
                    break

            composto_da = ''
            for c in CompostoDa.objects.filter(nome_menu=x, cod_locale=cod_locale):
                composto_da += c.nome_prodotto.nome_prodotto + ', '
            composto_da = composto_da[::-1].replace(' ,', '', 1)[::-1]
            self.menu_list.append({'menu': x, 'pos': pos, 'form': form, 'composto_da': composto_da, })
            pos += 1
        vote = {'avg': str(round(avg_vote, 2)).replace('.', ','), 'count': count_vote}
        dealers = []
        for dealer in Commerciante.objects.filter(possiede_locale__cod_locale=cod_locale).all():
            dealers.append({'first_name': User.objects.get(username=dealer).first_name,
                            'last_name': User.objects.get(username=dealer).last_name,
                            'username': User.objects.get(username=dealer).username,
                            })
        num_obj = 0
        for el in self.prod_ordine:
            num_obj += el['num_obj']
        for el in self.menu_ordine:
            num_obj += el['num_obj']

        tags = '- '
        for elem in local.tag.all().values_list():
            tags += elem[0] + ', '
        args = {'local': local, 'location': location, 'vote': vote, 'dealers': dealers,
                'dealers_id': [dealer.user.id for dealer in
                               Commerciante.objects.filter(possiede_locale__cod_locale=cod_locale).all()],
                'photo_list': photo_list, 'photo_len': photos.__len__(),
                'prod_list': self.prod_list, 'menu_list': self.menu_list,
                'prod_ordine': self.prod_ordine, 'menu_ordine': self.menu_ordine, 'num_obj': num_obj,
                'tags': tags.rsplit(', ', 1)[0] + ' -'
                }
        return args

    @classmethod
    def get(cls, request, cod_locale):
        if cls.last_user is not request.user or cls.last_local is not cod_locale:
            cls.menu_ordine = []
            cls.prod_ordine = []
            cls.prod_list = []
            cls.menu_list = []
            cls.last_local = cod_locale
            cls.last_user = request.user
        cls.init_obj(cls, cod_locale)
        args = cls.local_lists(cls, cod_locale)
        return render(request, cls.template_name, args)

    @classmethod
    def post(cls, request, cod_locale):
        cls.last_local = cod_locale
        if cls.prod_ordine == [] and cls.menu_ordine == []:
            cls.init_obj(cls, cod_locale)
        if request.method == 'POST':
            form = QuantityForm(request.POST or None)
            if form.is_valid():
                if form.cleaned_data['isProduct']:
                    for x in cls.prod_ordine:
                        if x['id'] == form.cleaned_data['id']:
                            x['num_obj'] = form.cleaned_data['num_object']
                else:
                    for x in cls.menu_ordine:
                        if x['id'] == form.cleaned_data['id']:
                            x['num_obj'] = form.cleaned_data['num_object']
        args = cls.local_lists(cls, cod_locale)
        return render(request, cls.template_name, args)


class Votes(View):
    template_name = 'localManagement/votes.html'
    user_form = ReviewForm
    update = False
    dealer_form = ReplayForm
    dealers = []

    @staticmethod
    def orderer_votes(self, vote):
        tree = []
        for rec in vote:
            if rec.voto is not None:
                if len(tree) != 0:
                    pos = -1
                    for elem_tree in tree:
                        if rec.date > elem_tree.date and elem_tree.voto is not None:
                            pos = tree.index(elem_tree)
                            if pos == len(tree):
                                tree.append(rec)
                            else:
                                tree.insert(pos, rec)
                            break
                    if pos == -1:
                        tree.append(rec)
                else:
                    tree.append(rec)
            else:
                for elem_tree in tree:
                    if elem_tree.email == rec.email:
                        pos = tree.index(elem_tree)
                        tree.insert(pos + 1, rec)
                        break
        return tree

    @classmethod
    def get(cls, request, cod_locale):
        local = get_object_or_404(Locale, pk=cod_locale)
        review = cls.orderer_votes(cls, Recensione.objects.filter(cod_locale=cod_locale).order_by('voto').all())

        for dealer in Commerciante.objects.filter(possiede_locale__cod_locale=cod_locale).all():
            cls.dealers.append(User.objects.get(username=dealer).username)
        if not request.user.is_anonymous:
            if request.user.is_utente:
                cls.user_form = ReviewForm()
                cls.update=False
                for rev in review:
                    if request.user == rev.email.user:
                        cls.user_form = ReviewForm(initial={'Voto': rev.voto, 'Descrizione': rev.descrizione})
                        cls.update = True
                        break
            elif request.user.is_commerciante \
                    and request.user in User.objects.filter(id__in=local.possiede_locale.all()):
                user_list = [(0, 'Seleziona un utente...'), ]
                for elem in Recensione.objects.filter(cod_locale=Locale.objects.get(pk=cod_locale), voto__gt=0):
                    user_list.append((elem.email.user.id, str(elem.email.user.username)), )
                cls.dealer_form = ReplayForm()
                cls.dealer_form.fields['Username'].choices = user_list

        tmp_cod_ordine = set()
        [tmp_cod_ordine.add(x.cod_ordine_id) for x in RichiedeP.objects.filter(cod_locale=cod_locale)]
        [tmp_cod_ordine.add(x.cod_ordine_id) for x in RichiedeM.objects.filter(cod_locale=cod_locale)]

        allow_rec = False
        if any([x.pk in list(tmp_cod_ordine) for x in OrdineInAttesa.objects.filter(email_id=request.user.pk)]):
            allow_rec = True

        args = {'local': local, 'vote': review, 'dealers': cls.dealers,
                'user_form': cls.user_form, 'dealer_form': cls.dealer_form,
                'allow_rec': allow_rec}
        return render(request, cls.template_name, args)

    @classmethod
    def post(cls, request, cod_locale):
        if request.method == 'POST':
            if request.user.is_utente:
                form = ReviewForm(request.POST or None)
                if form.is_valid():
                    voto = form.cleaned_data['Voto']
                    descrizione = form.cleaned_data['Descrizione']
                    if not cls.update:
                        Recensione.objects.create(voto=voto, descrizione=descrizione,
                                                  date=datetime.datetime.now().date(),
                                                  cod_locale=Locale.objects.get(pk=cod_locale),
                                                  email=Utente.objects.get(pk=User.objects.get(username=request.user)))
                    else:
                        Recensione.objects.filter(cod_locale=Locale.objects.get(pk=cod_locale), voto__gt=0,
                                                  email=Utente.objects.get(
                                                      pk=User.objects.get(username=request.user))).update(
                            voto=voto, descrizione=descrizione, date=datetime.datetime.now().date())
                        cls.update = False
            elif request.user.is_commerciante:
                form = ReplayForm(request.POST or None)
                descrizione = form.data['Descrizione']
                username = form.data['Username']
                if username == '0':
                    return redirect('localManagement:votes', cod_locale)
                if Recensione.objects.filter(voto=None, cod_locale=cod_locale, email_id=username).count():
                    Recensione.objects.filter(cod_locale=Locale.objects.get(pk=cod_locale), voto=None,
                                              email=Utente.objects.get(pk=username)). \
                        update(descrizione=descrizione, date=datetime.datetime.now().date(),
                               p_iva=Commerciante.objects.get(pk=User.objects.get(username=request.user)))
                else:
                    Recensione.objects.create(descrizione=descrizione,
                                              date=datetime.datetime.now().date(),
                                              cod_locale=Locale.objects.get(pk=cod_locale),
                                              email=Utente.objects.get(pk=username),
                                              p_iva=Commerciante.objects.get(
                                                  pk=User.objects.get(username=request.user)))
        return redirect('localManagement:votes', cod_locale)


class CreateLocalView(View):
    template_name = 'localManagement/nuovo_locale.html'
    model = get_user_model()
    form_class = CreateLocalForm

    def get(self, request):
        if request.user.is_anonymous or not request.user.is_commerciante:
            return redirect('/')

        comm = Commerciante.objects.exclude(user_id=request.user.id)
        form = CreateLocalForm()
        form.fields['altri_proprietari'].queryset = comm
        mex = "Aggiungi qui il tuo locale"
        context = {'form': form, 'mex': mex}
        return render(request, self.template_name, context)

    def post(self, request):
        if request.method == 'POST':
            form = CreateLocalForm(request.POST or None, request.FILES or None)
            messaggio = "Il locale e' stato aggiunto con successo"
            url = "Clicca qui per tornare all'area utente"
            context = {'messaggio': messaggio, 'url': url}

            if form.is_valid():
                nome_locale = form.cleaned_data['nome_locale']
                orario_apertura = form.cleaned_data['orario_apertura']
                orario_chiusura = form.cleaned_data['orario_chiusura']
                num_civico = form.cleaned_data['num_civico']
                via = form.cleaned_data['via']
                cap = form.cleaned_data['cap']
                descrizione = form.cleaned_data['descrizione']
                telefono = form.cleaned_data['telefono']
                sito_web = form.cleaned_data['sito_web']
                email = form.cleaned_data['email']
                prezzo_di_spedizione = form.cleaned_data['prezzo_di_spedizione']
                tag = form.cleaned_data['tag']
                giorno_chiusura = form.cleaned_data['giorno_chiusura']
                altri_proprietari = form.cleaned_data['altri_proprietari']
                foto_locale1 = form.cleaned_data['foto_locale1']
                foto_locale2 = form.cleaned_data['foto_locale2']
                foto_locale3 = form.cleaned_data['foto_locale3']
                # geocoding ---------------------
                latitude, longitude = geocode(str(via) + ',' + str(num_civico) + ',' + str(cap) + 'Italia')

                if Locale.objects.filter(nome_locale=nome_locale, cap=cap).exists():
                    messaggio = "Errore"
                    messaggio1 = "Esiste gia' un locale col nome inserito nella localita' inserita!"
                    messaggio2 = "Si prega di reinserire i dati correttamente"
                    url = "Clicca qui per tornare alla pagina di aggiunta di un locale"
                    context = {'messaggio': messaggio, 'messaggio1': messaggio1, 'messaggio2': messaggio2, 'url': url}
                    return render(request, 'localManagement/successo_insuccesso_locale.html', context)
                elif Locale.objects.filter(telefono=telefono).exists():
                    messaggio = "Errore"
                    messaggio1 = "Esiste gia' un locale col numero di telefono inserito!"
                    messaggio2 = "Si prega di reinserire i dati correttamente"
                    url = "Clicca qui per tornare alla pagina di aggiunta di un locale"
                    context = {'messaggio': messaggio, 'messaggio1': messaggio1, 'messaggio2': messaggio2, 'url': url}
                    return render(request, 'localManagement/successo_insuccesso_locale.html', context)
                elif Locale.objects.filter(email=email).exists():
                    messaggio = "Errore"
                    messaggio1 = "Esiste gia' un locale con l'indirizzo email inserito!"
                    messaggio2 = "Si prega di reinserire i dati correttamente"
                    url = "Clicca qui per tornare alla pagina di aggiunta di un locale"
                    context = {'messaggio': messaggio, 'messaggio1': messaggio1, 'messaggio2': messaggio2, 'url': url}
                    return render(request, 'localManagement/successo_insuccesso_locale.html', context)
                else:
                    t = Tag.objects.filter(nome_tag__in=tag)

                    # geocoding -----------------------------

                    loc = Locale(nome_locale=nome_locale,
                                 orario_apertura=orario_apertura,
                                 orario_chiusura=orario_chiusura,
                                 num_civico=num_civico, via=via,
                                 cap=Localita.objects.get(cap=cap.cap),
                                 descrizione=descrizione,
                                 telefono=telefono,
                                 sito_web=sito_web, email=email,
                                 prezzo_di_spedizione=prezzo_di_spedizione,
                                 latitude=latitude, longitude=longitude)

                    if loc.correct_open_close_time():

                        # loc = Locale.objects.create(nome_locale=nome_locale, orario_apertura=orario_apertura,
                        #                             orario_chiusura=orario_chiusura, num_civico=num_civico, via=via,
                        #                             cap=Localita.objects.get(cap=cap.cap), descrizione=descrizione,
                        #                             telefono=telefono,
                        #                             sito_web=sito_web, email=email,
                        #                             prezzo_di_spedizione=prezzo_di_spedizione,
                        #                             latitude=latitude, longitude=longitude)
                        loc.save()
                        loc.tag.set(t)

                        if giorno_chiusura is not None:
                            for x in giorno_chiusura:
                                Chiusura.objects.create(cod_locale=Locale.objects.get(cod_locale=loc.cod_locale),
                                                        giorno_chiusura=x)

                        comm = Commerciante.objects.get(user_id=request.user.id)
                        comm.possiede_locale.add(Locale.objects.get(cod_locale=loc.cod_locale))
                        if altri_proprietari is not None:
                            for x in altri_proprietari:
                                x.possiede_locale.add(Locale.objects.get(cod_locale=loc.cod_locale))

                        foto1 = FotoLocale(cod_locale=loc, foto_locale=foto_locale1)
                        foto1.save()
                        if foto_locale2 is not None:
                            foto2 = FotoLocale(cod_locale=loc, foto_locale=foto_locale2)
                            foto2.save()
                        if foto_locale3 is not None:
                            foto3 = FotoLocale(cod_locale=loc, foto_locale=foto_locale3)
                            foto3.save()

                        return render(request, 'localManagement/successo_insuccesso_locale.html', context)
                    else:
                        messaggio = 'Errore'
                        messaggio1 = 'Si prega di reinserire correttamente i dati'
                        messaggio2 = 'Ricordarsi che l\'orario di apertura non puo\' essere successivo a quello di chiusura'
                        context = {"form": form, "messaggio": messaggio, 'messaggio1': messaggio1,
                                   'messaggio2': messaggio2, 'url': url}
                        return render(request, 'localManagement/successo_insuccesso_locale.html', context)

            messaggio = 'Errore'
            messaggio1 = 'Si prega di reinserire i dati'
            context = {"form": form, "messaggio": messaggio, 'messaggio1': messaggio1, 'url': url}
            return render(request, 'localManagement/successo_insuccesso_locale.html', context)


class EditLocalView(View):
    template_name = 'localManagement/nuovo_locale.html'
    model = Locale
    form_class = EditLocal

    def get(self, request, cod_locale):
        if request.user.is_anonymous or not request.user.is_commerciante:
            return redirect('/')

        loc = Locale.objects.get(cod_locale=cod_locale)
        fot = FotoLocale.objects.filter(cod_locale=cod_locale)
        comm = Commerciante.objects.exclude(user_id=request.user.id)
        dealers = []
        for dealer in Commerciante.objects.filter(possiede_locale__cod_locale=cod_locale).exclude(
                user_id=request.user.id):
            dealers.append(User.objects.get(username=dealer).username)

        mex = 'Modifica qui il tuo locale'
        id = []
        indx = 0

        for f in fot:
            id.append(f.id)
            indx += 1

        data = {'cod_locale': loc.cod_locale, 'nome_locale': loc.nome_locale, 'orario_apertura': loc.orario_apertura,
                'orario_chiusura': loc.orario_chiusura, 'cap': loc.cap, 'via': loc.via, 'num_civico': loc.num_civico,
                'descrizione': loc.descrizione, 'telefono': loc.telefono, 'sito_web': loc.sito_web,
                'email': loc.email, 'prezzo_di_spedizione': loc.prezzo_di_spedizione}

        if indx == 1:
            d1 = {'foto_locale1': FotoLocale.objects.get(id=id[indx - 1]).foto_locale}
            z = dict(data)
            z.update(d1)
            form = EditLocal(request.FILES or None, initial=z)
            form.fields['altri_proprietari'].queryset = comm
            context = {'form': form, 'loc': loc, 'mex': mex}
            return render(request, self.template_name, context)
        elif indx == 2:
            d2 = {'foto_locale1': FotoLocale.objects.get(id=id[indx - 2]).foto_locale,
                  'foto_locale2': FotoLocale.objects.get(id=id[indx - 1]).foto_locale}
            z = dict(data)
            z.update(d2)
            form = EditLocal(request.FILES or None, initial=z)
            form.fields['altri_proprietari'].queryset = comm
            context = {'form': form, 'loc': loc, 'mex': mex}
            return render(request, self.template_name, context)
        elif indx == 3:
            d3 = {'foto_locale1': FotoLocale.objects.get(id=id[indx - 3]).foto_locale,
                  'foto_locale2': FotoLocale.objects.get(id=id[indx - 2]).foto_locale,
                  'foto_locale3': FotoLocale.objects.get(id=id[indx - 1]).foto_locale}
            z = dict(data)
            z.update(d3)
            form = EditLocal(request.FILES or None, initial=z)
            form.fields['altri_proprietari'].queryset = comm
            context = {'form': form, 'loc': loc, 'mex': mex}
            return render(request, self.template_name, context)
        else:
            form = EditLocal(request.FILES or None, initial=data)
            form.fields['altri_proprietari'].queryset = comm
            context = {'form': form, 'loc': loc, 'mex': mex}
            return render(request, self.template_name, context)

    def post(self, request, cod_locale):
        form = EditLocal(request.POST or None, request.FILES or None)
        messaggio = "Il locale e' stato modificato con successo"
        url = "Clicca qui per tornare all'area utente"
        context = {'messaggio': messaggio, 'url': url}
        if request.method == 'POST':
            if form.is_valid():
                nome_locale = form.cleaned_data['nome_locale']
                orario_apertura = form.cleaned_data['orario_apertura']
                orario_chiusura = form.cleaned_data['orario_chiusura']
                num_civico = form.cleaned_data['num_civico']
                via = form.cleaned_data['via']
                cap = form.cleaned_data['cap']
                descrizione = form.cleaned_data['descrizione']
                telefono = form.cleaned_data['telefono']
                sito_web = form.cleaned_data['sito_web']
                email = form.cleaned_data['email']
                prezzo_di_spedizione = form.cleaned_data['prezzo_di_spedizione']
                tag = form.cleaned_data['tag']
                giorno_chiusura = form.cleaned_data['giorno_chiusura']
                altri_proprietari = form.cleaned_data['altri_proprietari']
                rimuovi_altri_proprietari = form.cleaned_data['rimuovi_altri_proprietari']
                foto_locale1 = form.cleaned_data['foto_locale1']
                foto_locale2 = form.cleaned_data['foto_locale2']
                foto_locale3 = form.cleaned_data['foto_locale3']
                latitude, longitude = geocode(str(via) + ',' + str(num_civico) + ',' + str(cap) + 'Italia')
                #  geocoding ------------------
                c = Locale(nome_locale=nome_locale,
                           orario_apertura=orario_apertura,
                           orario_chiusura=orario_chiusura,
                           num_civico=num_civico, via=via,
                           cap=Localita.objects.get(cap=cap.cap),
                           descrizione=descrizione,
                           telefono=telefono,
                           sito_web=sito_web, email=email,
                           prezzo_di_spedizione=prezzo_di_spedizione,
                           latitude=latitude, longitude=longitude)

                if c.correct_open_close_time():

                    Locale.objects.filter(cod_locale=cod_locale).update(nome_locale=nome_locale,
                                                                        orario_apertura=orario_apertura,
                                                                        orario_chiusura=orario_chiusura,
                                                                        num_civico=num_civico, via=via,
                                                                        cap=Localita.objects.get(cap=cap.cap),
                                                                        descrizione=descrizione,
                                                                        telefono=telefono,
                                                                        sito_web=sito_web, email=email,
                                                                        prezzo_di_spedizione=prezzo_di_spedizione,
                                                                        latitude=latitude, longitude=longitude)
                    id = []
                    indx = 0
                    for f in FotoLocale.objects.all():
                        id.append(f.id)
                        indx += 1

                    if foto_locale1 is not None:
                        if indx is 1:
                            FotoLocale.objects.get(id=id[0]).delete()
                        foto1 = FotoLocale.objects.create(cod_locale=Locale.objects.get(cod_locale=cod_locale),
                                                          foto_locale=foto_locale1)
                        foto1.save()
                    if foto_locale2 is not None:
                        if indx is 2:
                            FotoLocale.objects.get(id=id[1]).delete()
                        foto2 = FotoLocale.objects.create(cod_locale=Locale.objects.get(cod_locale=cod_locale),
                                                          foto_locale=foto_locale2)
                        foto2.save()
                    if foto_locale3 is not None:
                        if indx is 3:
                            FotoLocale.objects.get(id=(id[2])).delete()
                        foto3 = FotoLocale.objects.create(cod_locale=Locale.objects.get(cod_locale=cod_locale),
                                                          foto_locale=foto_locale3)
                        foto3.save()

                    loc = Locale.objects.get(cod_locale=cod_locale)
                    if giorno_chiusura:
                        Chiusura.objects.filter(cod_locale=Locale.objects.get(cod_locale=loc.cod_locale)).delete()
                        for i in giorno_chiusura:
                            Chiusura.objects.create(cod_locale=Locale.objects.get(cod_locale=cod_locale),
                                                    giorno_chiusura=i)

                    if tag:
                        Locale.tag.through.objects.filter(locale_id=cod_locale).delete()
                        for x in tag:
                            loc.tag.add(Tag.objects.get(nome_tag=x))

                    comm = Commerciante.objects.get(user_id=request.user.id)
                    comm.possiede_locale.add(Locale.objects.get(cod_locale=loc.cod_locale))
                    if altri_proprietari is not None:
                        for x in altri_proprietari:
                            x.possiede_locale.add(Locale.objects.get(cod_locale=loc.cod_locale))

                    if rimuovi_altri_proprietari:
                        a = Commerciante.possiede_locale.through.objects.filter(locale_id=cod_locale).exclude(
                            commerciante_id=request.user.id).delete()

                    return render(request, 'localManagement/successo_insuccesso_locale.html', context)
                else:
                    messaggio = 'Insuccesso'
                    messaggio1 = 'L\'orario di apertura non puo\' essere successivo a quello di chiusura'
                    context = {"form": form, "messaggio": messaggio, 'messaggio1': messaggio1, 'url': url}
                    return render(request, 'localManagement/successo_insuccesso_locale.html', context)
            else:
                messaggio = 'Insuccesso'
                messaggio1 = 'Riprovare'
                context = {"form": form, "messaggio": messaggio, 'messaggio1': messaggio1, 'url': url}
                return render(request, 'localManagement/successo_insuccesso_locale.html', context)


class DeleteLocal(View):
    def get(self, request, cod_locale):
        if request.user.is_anonymous or not request.user.is_commerciante:
            return redirect('/')

        if Locale.objects.filter(cod_locale=cod_locale).delete():
            messaggio = 'Successo'
            messaggio1 = "Il locale e' stato rimosso con successo"
            red = "'accounts:dashboard'"
            url = "Clicca qui per tornare alla dashboard"
            context = {'messaggio': messaggio, 'messaggio1': messaggio1, 'red': red, 'url': url}
            return render(request, 'localManagement/successo_insuccesso_locale.html', context)
        else:
            messaggio = 'Insuccesso'
            messaggio1 = "Il locale non e' stato rimosso con successo"
            red = "accounts:dashboard"
            url = "Clicca qui per tornare alla dashboard"
            context = {'messaggio': messaggio, 'messaggio1': messaggio1, 'red': red, 'url': url}
            return render(request, 'localManagement/successo_insuccesso_locale.html', context)


class ProductsList(View):
    def get(self, request, cod_locale):
        if request.user.is_anonymous or not request.user.is_commerciante:
            return redirect('/')

        prod = Prodotto.objects.filter(cod_locale=cod_locale)
        context = {"prod": prod, "cl": cod_locale, 'locale': Locale.objects.get(pk=cod_locale)}
        return render(request, 'localManagement/product_list.html', context)


class AddProduct(View):
    form_class = AddEProduct

    @classmethod
    def get(cls, request, cod_locale):
        if request.user.is_anonymous or not request.user.is_commerciante:
            return redirect('/')

        form = AddEProduct()
        context = {'form': form, 'locale': Locale.objects.get(pk=cod_locale)}
        return render(request, 'localManagement/aggiunta_prodotto.html', context)

    @classmethod
    def post(cls, request, cod_locale):
        form = AddEProduct(request.POST or None, request.FILES or None)
        messaggio = "L'aggiunta del prodotto e' avvenuta con successo"
        url = "Clicca qui per tornare alla pagina dei prodotti"
        context = {'messaggio': messaggio, 'url': url, 'cl': cod_locale, 'locale': Locale.objects.get(pk=cod_locale)}
        if request.method == 'POST':
            if form.is_valid():
                nome_prodotto = form.cleaned_data['nome_prodotto']
                descrizione_prodotto = form.cleaned_data['descrizione_prodotto']
                prezzo = form.cleaned_data['prezzo']
                foto_prodotto = form.cleaned_data['foto_prodotto']

                if Prodotto.objects.filter(nome_prodotto=nome_prodotto, cod_locale=cod_locale).exists():
                    messaggio = "Esiste gia' un prodotto con lo stesso nome per il locale selezionato. Cambiare e ripovare."
                    url = "Clicca qui per tornare alla pagina dei prodotti"
                    context = {'messaggio': messaggio, 'url': url, 'cl': cod_locale,
                               'locale': Locale.objects.get(pk=cod_locale)}
                    return render(request, 'localManagement/successo_aggiunta_prodotto.html', context)

                Prodotto.objects.create(nome_prodotto=nome_prodotto, descrizione_prodotto=descrizione_prodotto,
                                        prezzo=prezzo, foto_prodotto=foto_prodotto, cod_locale_id=cod_locale)
                return render(request, 'localManagement/successo_aggiunta_prodotto.html', context)
            else:
                messaggio = "Errore nell'aggiunta del prodotto. Riprovare inserendo correttamente i campi"
                url = "Clicca qui per tornare alla pagina dei prodotti"
                context = {'messaggio': messaggio, 'url': url, 'cl': cod_locale,
                           'locale': Locale.objects.get(pk=cod_locale)}
                return render(request, 'localManagement/successo_aggiunta_prodotto.html', context)


class ProductsMod(View):
    form_class = EditProduct

    @classmethod
    def get(cls, request, cod_locale, id):
        if request.user.is_anonymous or not request.user.is_commerciante:
            return redirect('/')

        prod = Prodotto.objects.get(id=id)
        initial = {'nome_prodotto': prod.nome_prodotto, 'descrizione_prodotto': prod.descrizione_prodotto,
                   'prezzo': prod.prezzo, 'foto_prodotto': prod.foto_prodotto}
        form = EditProduct(initial=initial)
        context = {'form': form, 'locale': Locale.objects.get(pk=cod_locale)}
        return render(request, 'localManagement/edit_product.html', context)

    @classmethod
    def post(cls, request, cod_locale, id):
        form = EditProduct(request.POST or None, request.FILES or None)
        messaggio = "La modifica del prodotto e' avvenuta con successo"
        url = "Clicca qui per tornare alla pagina dei prodotti"
        context = {'messaggio': messaggio, 'url': url, 'locale': Locale.objects.get(pk=cod_locale)}
        if request.method == 'POST':
            if form.is_valid():
                nome_prodotto = form.cleaned_data['nome_prodotto']
                descrizione_prodotto = form.cleaned_data['descrizione_prodotto']
                prezzo = form.cleaned_data['prezzo']
                foto_prodotto = form.cleaned_data['foto_prodotto']
                foto_prod = Prodotto.objects.get(id=id).foto_prodotto
                print(foto_prod)
                Prodotto.objects.filter(id=id).delete()

                if Prodotto.objects.filter(nome_prodotto=nome_prodotto, cod_locale=cod_locale).exists():
                    messaggio = "Esiste gia' un prodotto con lo stesso nome per il locale selezionato. Cambiare e ripovare."
                    url = "Clicca qui per tornare alla pagina dei prodotti"
                    context = {'messaggio': messaggio, 'url': url, 'cl': cod_locale,
                               'locale': Locale.objects.get(pk=cod_locale)}
                    return render(request, 'localManagement/successo_aggiunta_prodotto.html', context)

                if foto_prodotto is not None:
                    Prodotto.objects.create(id=id, nome_prodotto=nome_prodotto,
                                            descrizione_prodotto=descrizione_prodotto,
                                            prezzo=prezzo, foto_prodotto=foto_prodotto,
                                            cod_locale_id=cod_locale)
                else:
                    Prodotto.objects.create(id=id, nome_prodotto=nome_prodotto,
                                            descrizione_prodotto=descrizione_prodotto,
                                            prezzo=prezzo, foto_prodotto=foto_prod,
                                            cod_locale_id=cod_locale)
                return render(request, 'localManagement/successo_aggiunta_prodotto.html', context)
            else:
                messaggio = "Errore nella modifica del prodotto. Riprovare inserendo correttamente i campi"
                url = "Clicca qui per tornare alla pagina dei prodotti"
                context = {'messaggio': messaggio, 'url': url, 'cl': cod_locale,
                           'locale': Locale.objects.get(pk=cod_locale)}
                return render(request, 'localManagement/successo_aggiunta_prodotto.html', context)


class DeleteProduct(View):
    def get(self, request, cod_locale, id):
        if request.user.is_anonymous or not request.user.is_commerciante:
            return redirect('/')

        if Prodotto.objects.filter(id=id).exists():
            messaggio = "l'eliminazione del prodotto e' avvenuta con successo"
            url = 'Clicca qui se invece vuoi tornare alla pagina dei tuoi prodotti'
            Prodotto.objects.filter(id=id).delete()
            context = {"cl": cod_locale, 'url': url, 'messaggio': messaggio,
                       'locale': Locale.objects.get(pk=cod_locale)}
            return render(request, 'localManagement/delete_product.html', context)
        else:
            messaggio = "Qualcosa e' andato storto, controllare che il prodotto esista e riprovare"
            url = "Clicca qui per tornare alla pagina dei menu"
            context = {'messaggio': messaggio, 'url': url, 'cl': cod_locale,
                       'locale': Locale.objects.get(pk=cod_locale)}
            return render(request, 'localManagement/successo_aggiunta_menu.html', context)


class MenuList(View):
    def get(self, request, cod_locale):
        if request.user.is_anonymous or not request.user.is_commerciante:
            return redirect('/')

        menu = Menu.objects.filter(cod_locale=cod_locale)
        context = {"menu": menu, "cl": cod_locale, 'locale': Locale.objects.get(pk=cod_locale)}
        return render(request, 'localManagement/lista_menu.html', context)


class AddMenu(View):
    form_class = AddEMenu

    @classmethod
    def get(cls, request, cod_locale):
        if request.user.is_anonymous or not request.user.is_commerciante:
            return redirect('/')

        prod = Prodotto.objects.filter(cod_locale=cod_locale)
        form = AddEMenu()
        form.fields['composto_da_prodotti'].queryset = prod
        context = {'form': form, 'locale': Locale.objects.get(pk=cod_locale)}
        return render(request, 'localManagement/aggiunta_menu.html', context)

    @classmethod
    def post(cls, request, cod_locale):
        form = AddEMenu(request.POST or None, request.FILES or None)
        messaggio = "L'aggiunta del menu e' avvenuta con successo"
        url = "Clicca qui per tornare alla pagina dei menu"
        context = {'messaggio': messaggio, 'url': url, 'cl': cod_locale, 'locale': Locale.objects.get(pk=cod_locale)}
        if request.method == 'POST':
            if form.is_valid():
                nome_menu = form.cleaned_data['nome_menu']
                descrizione_menu = form.cleaned_data['descrizione_menu']
                prezzo = form.cleaned_data['prezzo']
                composto_da_prodotti = form.cleaned_data['composto_da_prodotti']

                if Menu.objects.filter(nome_menu=nome_menu, cod_locale=cod_locale).exists():
                    messaggio = "Esiste gia' un menu con lo stesso nome per il locale selezionato. Cambiare e ripovare."
                    url = "Clicca qui per tornare alla pagina dei menu"
                    context = {'messaggio': messaggio, 'url': url, 'cl': cod_locale,
                               'locale': Locale.objects.get(pk=cod_locale)}
                    return render(request, 'localManagement/successo_aggiunta_menu.html', context)

                mymenu = Menu.objects.create(cod_locale=Locale.objects.get(cod_locale=cod_locale), nome_menu=nome_menu,
                                             descrizione_menu=descrizione_menu, prezzo=prezzo)

                l_prod = composto_da_prodotti.__len__()

                for x in range(l_prod):
                    CompostoDa.objects.create(cod_locale=Locale.objects.get(cod_locale=cod_locale),
                                              nome_menu=Menu.objects.get(nome_menu=mymenu.nome_menu),
                                              nome_prodotto=Prodotto.objects.get(nome_prodotto=composto_da_prodotti[x],
                                                                                 cod_locale=cod_locale), )

                return render(request, 'localManagement/successo_aggiunta_menu.html', context)
            else:
                messaggio = "Qualcosa e' andato storto, inserire i dati in maniera corretta e riprovare"
                url = "Clicca qui per tornare alla pagina dei menu"
                context = {'messaggio': messaggio, 'url': url, 'cl': cod_locale,
                           'locale': Locale.objects.get(pk=cod_locale)}
                return render(request, 'localManagement/successo_aggiunta_menu.html', context)


class DeleteMenu(View):
    def get(self, request, cod_locale, id):
        if request.user.is_anonymous or not request.user.is_commerciante:
            return redirect('/')

        if Menu.objects.filter(id=id).exists():
            url = 'Clicca qui se invece vuoi tornare alla pagina dei tuoi menu'
            messaggio = "Il menu' e' stato eliminato con successo"
            Menu.objects.filter(id=id).delete()
            context = {"cl": cod_locale, 'url': url, 'messaggio': messaggio,
                       'locale': Locale.objects.get(pk=cod_locale)}
            return render(request, 'localManagement/successo_aggiunta_menu.html', context)
        else:
            messaggio = "Qualcosa e' andato storto, controllare che il menu esista e riprovare"
            url = "Clicca qui per tornare alla pagina dei menu"
            context = {'messaggio': messaggio, 'url': url, 'cl': cod_locale,
                       'locale': Locale.objects.get(pk=cod_locale)}
            return render(request, 'localManagement/successo_aggiunta_menu.html', context)


class EditMenu(View):
    form_class = ModMenu

    @classmethod
    def get(cls, request, cod_locale, id):
        if request.user.is_anonymous or not request.user.is_commerciante:
            return redirect('/')

        prod = Prodotto.objects.filter(cod_locale=cod_locale)
        menu = Menu.objects.get(id=id)
        initial = {'nome_menu': menu.nome_menu, 'descrizione_menu': menu.descrizione_menu,
                   'prezzo': menu.prezzo}
        form = ModMenu(initial=initial)
        form.fields['composto_da_prodotti'].queryset = prod
        context = {'form': form, 'locale': Locale.objects.get(pk=cod_locale)}
        return render(request, 'localManagement/aggiunta_menu.html', context)

    @classmethod
    def post(cls, request, cod_locale, id):
        form = ModMenu(request.POST or None, request.FILES or None)
        messaggio = "La modifica del menu e' avvenuta con successo"
        url = "Clicca qui per tornare alla pagina dei menu"
        context = {'messaggio': messaggio, 'url': url, 'cl': cod_locale, 'locale': Locale.objects.get(pk=cod_locale)}
        if request.method == 'POST':
            if form.is_valid():
                nome_menu = form.cleaned_data['nome_menu']
                descrizione_menu = form.cleaned_data['descrizione_menu']
                prezzo = form.cleaned_data['prezzo']
                composto_da_prodotti = form.cleaned_data['composto_da_prodotti']
                id = Menu.objects.get(id=id).id
                Menu.objects.filter(id=id).delete()

                if Menu.objects.filter(nome_menu=nome_menu, cod_locale=cod_locale).exists():
                    messaggio = "Esiste gia' un menu con lo stesso nome per il locale selezionato. Cambiare e ripovare."
                    url = "Clicca qui per tornare alla pagina dei menu"
                    context = {'messaggio': messaggio, 'url': url, 'cl': cod_locale,
                               'locale': Locale.objects.get(pk=cod_locale)}
                    return render(request, 'localManagement/successo_aggiunta_menu.html', context)

                mymenu = Menu.objects.create(id=id, cod_locale=Locale.objects.get(cod_locale=cod_locale),
                                             nome_menu=nome_menu,
                                             descrizione_menu=descrizione_menu,
                                             prezzo=prezzo)

                l_prod = composto_da_prodotti.__len__()

                if composto_da_prodotti is not None:
                    CompostoDa.objects.filter(cod_locale=Locale.objects.get(cod_locale=cod_locale),
                                              nome_menu=Menu.objects.get(nome_menu=mymenu.nome_menu)).delete()
                    for x in range(l_prod):
                        CompostoDa.objects.create(cod_locale=Locale.objects.get(cod_locale=cod_locale),
                                                  nome_menu=Menu.objects.get(nome_menu=mymenu.nome_menu),
                                                  nome_prodotto=Prodotto.objects.get(
                                                      nome_prodotto=composto_da_prodotti[x]))
                return render(request, 'localManagement/successo_aggiunta_menu.html', context)
            else:
                messaggio = "Qualcosa e' andato storto, inserire i dati in maniera corretta e riprovare"
                url = "Clicca qui per tornare alla pagina dei menu"
                context = {'messaggio': messaggio, 'url': url, 'cl': cod_locale,
                           'locale': Locale.objects.get(pk=cod_locale)}
                return render(request, 'localManagement/successo_aggiunta_menu.html', context)
