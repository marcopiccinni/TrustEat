from django.test import TestCase
from user.models import CartaDiCredito
import datetime


class CardsTests(TestCase):

    def test_card_valid(self):
        card = CartaDiCredito(numero_carta='14351341341', intestatario='prova', scadenza=datetime.date(2019, 12, 1))
        self.assertEqual(card.is_valid(), True)
