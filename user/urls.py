from django.urls import path
from . import views
from django.conf.urls import url
from .views import DeleteCard, AddCreditCard

app_name = 'user'

urlpatterns = [
    path('add_credit_card', AddCreditCard.as_view(), name='add_cc'),
    url(r'^(?P<cod_carta>[0-9]+)/remove_credit_card$', DeleteCard.as_view(), name='remove_cc'),
]
