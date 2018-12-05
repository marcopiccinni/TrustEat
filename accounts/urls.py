from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import *
from localManagement.views import CreateLocalView
from django.conf.urls import url

app_name = 'accounts'

urlpatterns = [
    # path('login/', views.user_login, name='login'),
    # url(r'^(?P<username>[A-Za-z0-9]+)/$', views.us, name='us'),
    path('commerciante/edit', EditCommDataView.as_view(), name='cedit'),
    path('utente/edit', EditPersonalDataView.as_view(), name='uedit'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registrazione/utente', RegUtenteView.as_view(), name='registrazione_utente'),
    path('registrazione/commerciante', RegCommercianteView.as_view(), name='registrazione_commerciante'),
    path('commerciante/registrazione_locale', CreateLocalView.as_view(), name='registrazione_locale'),
    path('', views.dashboard, name='dashboard'),
    path('area_utente', AreaUtente.as_view(), name='area_utente'),
    path('registrazione/login_social', InsertLogin.as_view(), name='registrazione_login_social'),
]
