from django.urls import path
from . import views
from .views import Check, PlacedOrder

app_name = 'order'

urlpatterns = [
    # path('', views.check, name='check'),
    path('', Check.as_view(), name='check'),
    path('placed/', PlacedOrder.as_view(), name='placed_order'),
]
