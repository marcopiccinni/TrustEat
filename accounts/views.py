from django.contrib.auth import login
from django.views.generic import CreateView, TemplateView, UpdateView, View
from .forms import *
from django.shortcuts import render, redirect, HttpResponse, render_to_response, HttpResponseRedirect
from .models import User, Commerciante, Utente
from order.models import OrdineInAttesa, RichiedeP, RichiedeM
from order.views import db_order_consistance
from django.contrib.auth import get_user_model, authenticate
from localManagement.models import Locale, Tag, FotoLocale, Chiusura, Localita
from django.contrib.auth.decorators import login_required
from user.models import CartaDiCredito


class RegUtenteView(CreateView):
    model = get_user_model()
    form_class = RegUser
    template_name = 'registration/registrazione_utente.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'utente'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return render_to_response('account/avviso_successo.html')


class RegCommercianteView(CreateView):
    model = User
    form_class = RegComm
    template_name = 'registration/registrazione_commerciante.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'commerciante'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        if user.is_commerciante:
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            return render_to_response('account/avviso_successo.html')
        else:
            u = User.objects.get(username=user.username)
            u.delete()
            return render_to_response('account/avviso_insuccesso.html')


@login_required
def dashboard(request):
    if not request.user.is_utente and not request.user.is_commerciante and not request.user.is_superuser:
        return HttpResponseRedirect('/accounts/registrazione/login_social')
    else:
        return redirect('/')


class InsertLogin(View):
    form = InsertLoginSocial()
    model = get_user_model()
    template_name = 'account/reindirizzamento_social_dati.html'
    form_class = InsertLoginSocial

    @login_required
    def get(self, request):
        form = InsertLoginSocial()
        return render(request, self.template_name, {'form': form})

    @login_required
    def post(self, request):
        if request.method == 'POST':
            form = InsertLoginSocial(request.POST or None)
            if form.is_valid():

                tipo_utente = form.cleaned_data['tipo_utente']
                via = form.cleaned_data['via']
                civico = form.cleaned_data['civico']
                cap = form.cleaned_data['cap']
                telefono = form.cleaned_data['telefono']
                # carta_di_credito = form.cleaned_data['carta_di_credito']
                p_iva = form.cleaned_data['p_iva']

                current_user = request.user
                current_user.via = via
                current_user.civico = civico
                current_user.cap = cap.cap
                current_user.telefono = telefono

                if tipo_utente == "utente":
                    current_user.is_utente = True
                    current_user.save(update_fields=['is_utente', 'via', 'civico', 'cap', 'telefono'])
                    # CartaDiCredito.objects.create(numero_carta=carta_di_credito)
                    Utente.objects.create(user=current_user)
                else:
                    current_user = request.user
                    current_user.is_commerciante = True
                    current_user.save(update_fields=['is_commerciante', 'via', 'civico', 'cap', 'telefono'])
                    Commerciante.objects.create(user=current_user, p_iva=p_iva)

                return render(request, 'account/avviso_successo.html')

        return render(request, 'account/avviso_insuccesso.html')


class EditPersonalDataView(View):
    template_name = 'account/edit_personal_data.html'
    form = EditPersonalData
    model = get_user_model()

    def get(self, request):
        data = {'email': request.user.email, 'nome': request.user.first_name, 'cognome': request.user.last_name,
                'via': request.user.via, 'civico': request.user.civico,
                'cap': request.user.cap, 'telefono': request.user.telefono}
        form = EditPersonalData(initial=data)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = EditPersonalData(request.POST or None)
        messaggio = "I dati personali sono stati modificati con successo"
        url = "Clicca qui per tornare alla home"
        context = {'messaggio': messaggio, 'url': url}

        if request.method == 'POST':
            if form.is_valid():
                email = form.cleaned_data['email']
                nome = form.cleaned_data['nome']
                cognome = form.cleaned_data['cognome']
                password1 = form.cleaned_data['password1']
                password2 = form.cleaned_data['password2']
                if password1 != password2:
                    form = EditPersonalData()
                    # AGGIUNGERE ERRORE NEL FORM
                    return render(request, self.template_name, {'form': form})

                via = form.cleaned_data['via']
                civico = form.cleaned_data['civico']
                cap = form.cleaned_data['cap']
                telefono = form.cleaned_data['telefono']

                if User.objects.filter(username=request.user.username).update(email=email, first_name=nome,
                                                                              last_name=cognome, via=via,
                                                                              civico=civico, cap=cap.cap,
                                                                              telefono=telefono):
                    u = User.objects.get(username=request.user.username)
                    u.set_password(password2)
                    u.save()
                    login(self.request, u, backend='django.contrib.auth.backends.ModelBackend')
                    return render(request, 'account/avviso_successo.html', context)
                else:
                    messaggio1 = 'Insuccesso'
                    messaggio2 = 'Riprovare'
                    context = {"form": form, "messaggio1": messaggio1, 'messaggio2': messaggio2, 'url': url}
                    u = User.objects.get(username=request.user.username)
                    login(self.request, u, backend='django.contrib.auth.backends.ModelBackend')
                    return render(request, 'account/avviso_insuccesso.html', context)


class EditCommDataView(View):
    template_name = 'account/edit_personal_data.html'
    form = EditCommData
    model = get_user_model()

    def get(self, request):
        data = {'email': request.user.email, 'nome': request.user.first_name, 'cognome': request.user.last_name,
                'via': request.user.via, 'civico': request.user.civico,
                'cap': request.user.cap, 'telefono': request.user.telefono,
                'p_iva': request.user.commerciante_user.p_iva}
        form = EditCommData(initial=data)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = EditCommData(request.POST or None)
        messaggio = "I dati personali sono stati modificati con successo"
        url = "Clicca qui per tornare alla home"
        context = {'messaggio': messaggio, 'url': url}

        if request.method == 'POST':
            if form.is_valid():
                email = form.cleaned_data['email']
                nome = form.cleaned_data['nome']
                cognome = form.cleaned_data['cognome']
                password1 = form.cleaned_data['password1']
                password2 = form.cleaned_data['password2']
                if password1 != password2:
                    form = EditCommData()
                    # AGGIUNGERE ERRORE NEL FORM
                    return render(request, self.template_name, {'form': form})

                via = form.cleaned_data['via']
                civico = form.cleaned_data['civico']
                cap = form.cleaned_data['cap']
                telefono = form.cleaned_data['telefono']
                p_iva = form.cleaned_data['p_iva']

                if User.objects.filter(username=request.user.username).update(email=email, first_name=nome,
                                                                              last_name=cognome,
                                                                              via=via,
                                                                              civico=civico, cap=cap.cap,
                                                                              telefono=telefono):
                    u = User.objects.get(username=request.user.username)
                    u.set_password(password2)
                    u.save()
                    Commerciante.objects.filter(pk=request.user.id).update(p_iva=p_iva)
                    login(self.request, u, backend='django.contrib.auth.backends.ModelBackend')
                    return render(request, 'account/avviso_successo.html', context)
                else:
                    messaggio1 = 'Insuccesso'
                    messaggio2 = 'Riprovare'
                    context = {"form": form, "messaggio1": messaggio1, 'messaggio2': messaggio2, 'url': url}
                    u = User.objects.get(username=request.user.username)
                    login(self.request, u, backend='django.contrib.auth.backends.ModelBackend')
                    return render(request, 'account/avviso_insuccesso.html', context)


class AreaUtente(View):
    template_name = 'account/dashboard.html'

    # @login_required()
    def get(self, request):
        if request.user.is_commerciante:
            if request.method == 'POST':
                pass
            args = {'commerciante': Commerciante.objects.get(pk=request.user.id),
                    'location': Localita.objects.get(pk=request.user.cap),
                    }
            return render(request, self.template_name, args)

        elif request.user.is_utente:
            orders = []
            for order in OrdineInAttesa.objects.filter(email_id=User.objects.get(
                    username=request.user).id).order_by('data', 'orario_richiesto').reverse():
                local = None
                if RichiedeP.objects.filter(cod_ordine=order).count():
                    local = RichiedeP.objects.filter(cod_ordine=order).last().cod_locale
                    orders.append({'order': order, 'local': local})
                elif RichiedeM.objects.filter(cod_ordine=order).count():
                    local = RichiedeM.objects.filter(cod_ordine=order).last().cod_locale
                    orders.append({'order': order, 'local': local})
                else:
                    print(order.cod_ordine)

            args = {'orders': orders,
                    'location': Localita.objects.get(pk=request.user.cap),
                    }
            return render(request, self.template_name, args)
        return redirect('/')

    def post(self, request):
        c = request.POST['num_order']
        RichiedeP.objects.filter(cod_ordine_id=c).delete()
        RichiedeM.objects.filter(cod_ordine_id=c).delete()
        OrdineInAttesa.objects.filter(cod_ordine=c).delete()
        return redirect('accounts:area_utente')