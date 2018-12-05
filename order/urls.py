from django.urls import path
from django.conf.urls import url
from . import views
from .views import Check, PlacedOrder, ReviewOrder

app_name = 'order'

urlpatterns = [
    # path('', views.check, name='check'),
    path('', Check.as_view(), name='check'),
    path('placed/', PlacedOrder.as_view(), name='placed_order'),
    url(r'review/(?P<cod_ordine>[0-9]+)/$', ReviewOrder.as_view(), name='review_order'),
]