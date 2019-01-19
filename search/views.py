from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from .forms import SearchForm
from user.models import Recensione
from localManagement.models import FotoLocale, Locale, Localita, Tag
from accounts.models import User
from order.views import db_order_consistance
import operator


class Ricerca(ListView):
    form = SearchForm()
    model = Localita
    form_class = SearchForm
    template_name = 'search/index.html'
    ordered = []
    pos = ''

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        db_order_consistance()
        form = SearchForm()

        if request.user.is_authenticated and not (request.user.is_superuser or request.user.is_staff):
            location = User.objects.get(username=request.user).cap
            try:
                self.sorting(Locale.objects.filter(cap=Localita.objects.get(cap=location)).all())
            except:
                print(location)
                print(User.objects.get(pk=request.user.pk))
                User.objects.filter(pk=request.user.pk).delete()
                return redirect('/')

            form = SearchForm(initial={'Position': Localita.objects.get(cap=location), 'Tag': None}, )
            self.pos = Localita.objects.get(cap=location).nome_localita
        else:
            self.sorting(Locale.objects.all())
        context = {'locals': self.ordered, 'SearchForm': form,
                   'location': self.pos, 'location_len': len(str(self.pos))}
        if request.method == 'GET':
            form = SearchForm(request.GET or None)
            if form.is_valid():
                part_name = form.cleaned_data['CercaNome']
                if not part_name:
                    location=form.cleaned_data['Position']
                    if location is not None:
                        self.sorting(Locale.objects.filter(cap=Localita.objects.get(nome_localita=location)).all())
                        self.pos = location
                    else:
                        self.sorting(Locale.objects.all())
                        self.pos = ''
                    tags = list(form.cleaned_data['Tag'].values_list('nome_tag'))
                    if tags:
                        tmp = []
                        for loc in self.ordered:
                            c = 0
                            for sl in list(
                                    Tag.objects.filter(locale_tag__cod_locale=loc['local'].pk).values_list('nome_tag')):
                                if sl in tags:
                                    c += 1
                            if c == len(tags):
                                tmp.append(loc)
                        self.ordered = tmp
                    context = {'locals': self.ordered, 'SearchForm': form, 'location': self.pos,
                               'location_len': len(str(self.pos))}
                # alternative
                else:
                    self.pos=''
                    locals = []
                    for l in Locale.objects.filter(nome_locale__icontains=part_name).order_by('nome_locale'):
                        voti = Recensione.objects.filter(cod_locale=l)
                        n_rec = vote = 0
                        if voti.count():
                            for el in voti:
                                if el.voto in range(6):
                                    vote += el.voto
                                    n_rec += 1
                        if n_rec:
                            vote = vote / n_rec
                        else:
                            vote = 0
                        f = ""
                        for foto in FotoLocale.objects.filter(cod_locale=l):
                            f = foto.foto_locale.url
                        locals.append(
                            {'local': l, 'voto': str(round(vote, 2)).replace('.', ','), 'n_rec': n_rec, 'foto': f})
                    context = {'locals': locals, 'SearchForm': form, 'location': self.pos,
                               'location_len': len(str(self.pos))}
        # end alternative
        return render(request, self.template_name, context)

    def sorting(self, locals_list):
        self.ordered = []
        for local in locals_list:
            voti = Recensione.objects.filter(cod_locale=local)
            n_rec = vote = 0
            if voti.count():
                for el in voti:
                    if el.voto in range(6):
                        vote += el.voto
                        n_rec += 1
            if n_rec:
                vote = vote / n_rec
            else:
                vote = 0
            f = ""
            for foto in FotoLocale.objects.filter(cod_locale=local):
                f = foto.foto_locale.url

            self.ordered.append({'local': local, 'voto': str(round(vote, 2)).replace('.', ','), 'n_rec': n_rec,
                                 'foto': f})
            self.ordered.sort(key=operator.itemgetter('n_rec'), reverse=True)
            self.ordered.sort(key=operator.itemgetter('voto'), reverse=True)
