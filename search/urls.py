from django.urls import path
from . import views
from django.conf.urls import url
from .views import Ricerca

app_name = 'search'

urlpatterns = [
    path('', Ricerca.as_view(), name='index'),
    # path('', views.index, name='index'),

]
