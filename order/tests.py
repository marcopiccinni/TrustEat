from django.test import TestCase
from .models import OrdineInAttesa
import datetime

# controlla che la data di creazione dell'ordine non sia nel passato o nel futuro
class OrdersTests(TestCase):

    def test_order_valid(self):
        ordine = OrdineInAttesa(email_id=2, data=datetime.datetime.now(), orario_richiesto='23:00',
                                metodo_pagamento='alla consegna')
        self.assertEqual(ordine.check_order_data(), True)

    def test_order_future(self):
        ordine = OrdineInAttesa(email_id=2, data=datetime.datetime.now() + datetime.timedelta(days=5),
                                orario_richiesto='23:00',
                                metodo_pagamento='alla consegna')
        self.assertEqual(ordine.check_order_data(), False)

    def test_order_past(self):
        ordine = OrdineInAttesa(email_id=2, data=datetime.datetime.now() - datetime.timedelta(days=5),
                                orario_richiesto='23:00',
                                metodo_pagamento='alla consegna')
        self.assertEqual(ordine.check_order_data(), False)
