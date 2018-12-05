from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Questa e' la pagina di gestione dell'utente")



#
# class RecUser(UpdateView):
#     template_name = 'localManagement/votes.html'
#     model =
#     form_class = Ed
#
#     def get(self, request, cod_locale):
#         loc = Locale.objects.get(cod_locale=cod_locale)
#         fot = FotoLocale.objects.get(cod_locale=cod_locale)
#         data = {'cod_locale': loc.cod_locale, 'nome_locale': loc.nome_locale, 'orario_apertura': loc.orario_apertura,
#                 'orario_chiusura': loc.orario_chiusura, 'cap': loc.cap, 'via': loc.via, 'num_civico': loc.num_civico,
#                 'descrizione': loc.descrizione, 'telefono': loc.telefono, 'sito': loc.sito_web, 'email': loc.email,
#                 'foto_locale': fot.foto_locale}
#
#         form = EditForm(request.FILES or None, initial=data)
#         return render(request, self.template_name, {'form': form})
#
#     def post(self, request, cod_locale):
#         if request.method == 'POST':
#
#             form = EditForm(request.POST or None, request.FILES or None)
#
#             url = "Clicca qui per tornare alla home"
#             context = {'messaggio': messaggio, 'url': url}
#
#             if form.is_valid():
