from django.urls import path
from . import views
from .views import *
from django.conf.urls import url

app_name = 'localManagement'

urlpatterns = [
    url(r'^(?P<cod_locale>[0-9]+)/$', LocalList.as_view(), name='localLists'),
    url(r'^(?P<cod_locale>[0-9]+)/votes/$', Votes.as_view(), name='votes'),
    url(r'^(?P<cod_locale>[0-9]+)/edit_local/$', EditLocal.as_view(), name='edit_local'),
    url(r'^(?P<cod_locale>[0-9]+)/products_list/$', ProductsList.as_view(), name='products_list'),
    url(r'^(?P<cod_locale>[0-9]+)/menu_list/$', MenuList.as_view(), name='menu_list'),
    url(r'^(?P<cod_locale>[0-9]+)/products_list/(?P<id>[0-9]+)/edit$', ProductsMod.as_view(), name='pro'),
    url(r'^(?P<cod_locale>[0-9]+)/menu_list/(?P<id>[0-9]+)/edit$', EditMenu.as_view(), name='edit_menu'),
    url(r'^(?P<cod_locale>[0-9]+)/products_list/add/$', AddProduct.as_view(), name='add'),
    url(r'^(?P<cod_locale>[0-9]+)/menu_list/add$', AddMenu.as_view(), name='add_menu'),
    url(r'^(?P<cod_locale>[0-9]+)/products_list/(?P<id>[0-9]+)/remove$', DeleteProduct.as_view(), name='remove'),
    url(r'^(?P<cod_locale>[0-9]+)/menu_list/(?P<id>[0-9]+)/remove$', DeleteMenu.as_view(), name='remove_menu'),
    path('', views.index, name='index'),
]
