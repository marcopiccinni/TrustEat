from django.test import TestCase
from user.models import CartaDiCredito
import datetime


class CardsTests(TestCase):

    def test_card_valid(self):
        card = CartaDiCredito(numero_carta='14351341341', intestatario='prova', scadenza=datetime.date(2030, 12, 1))
        self.assertEqual(card.is_valid(), True)

    def test_card_past(self):
        card = CartaDiCredito(numero_carta='14351341341', intestatario='prova', scadenza=datetime.date(2016, 12, 1))
        self.assertEqual(card.is_valid(), False)

    def test_card_equal(self):
        card = CartaDiCredito(numero_carta='14351341341', intestatario='prova', scadenza=datetime.datetime.today())
        self.assertEqual(card.is_valid(), True)
