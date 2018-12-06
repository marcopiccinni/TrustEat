from django.urls import path
from django.conf.urls import url
from .views import Check, PlacedOrder, ReviewOrder, ListOrder

app_name = 'order'

urlpatterns = [
    path('', Check.as_view(), name='check'),
    path('placed/', PlacedOrder.as_view(), name='placed_order'),
    url(r'review/(?P<cod_ordine>[0-9]+)/$', ReviewOrder.as_view(), name='review_order'),
    url(r'list/(?P<cod_locale>[0-9]+)/$', ListOrder.as_view(), name='list_order')
]
