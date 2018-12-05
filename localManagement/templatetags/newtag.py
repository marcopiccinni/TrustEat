from django import template
from localManagement.models import Locale
from localManagement.views import LocalList

register = template.Library()


@register.simple_tag
def multiply(var1, var2):
    # return var1 * var2
    return str(var1 * var2).replace('.', ',')


@register.simple_tag
def total_price():
    sum_price = 0.00
    for elem in LocalList.prod_ordine:
        sum_price += float(elem['num_obj'] * elem['prodotto'].prezzo)
    for elem in LocalList.menu_ordine:
        sum_price += float(elem['num_obj'] * elem['menu'].prezzo)
    if sum_price > 0:
        sum_price += Locale.objects.get(cod_locale=LocalList.last_local).prezzo_di_spedizione
    if (round(sum_price, 2) - int(sum_price)) * 100 > 0:
        return str(round(sum_price, 2)).replace('.', ',')
    return int(sum_price)
