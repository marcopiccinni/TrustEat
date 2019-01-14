from django.test import TestCase
from .models import Locale, Localita


class LocalsTests(TestCase):

    # Assert ritorna True se effettivamente l'orario di apertura è minore dell'orario di chiusura
    def test_orario_lower(self):
        Localita.objects.create(cap='41100', nome_localita='Modena')
        local = Locale(nome_locale='Prova', orario_apertura='10:50', orario_chiusura='13:50',
                       cap=Localita.objects.get(nome_localita='Modena'), via='viale Italia', num_civico=3,
                       telefono='059000000',
                       )
        self.assertEqual(local.correct_open_close_time(), True)

    def test_orario_equal(self):
        Localita.objects.create(cap='41100', nome_localita='Modena')
        local = Locale(nome_locale='Prova', orario_apertura='13:50', orario_chiusura='13:50',
                       cap=Localita.objects.get(nome_localita='Modena'), via='viale Italia', num_civico=3,
                       telefono='059000000',
                       )
        local.save()
        print(Locale.objects.all())
        self.assertEqual(local.orario_apertura < local.orario_chiusura, False)

    def test_orario_greater(self):
        Localita.objects.create(cap='41100', nome_localita='Modena')
        local = Locale(nome_locale='Prova', orario_apertura='13:50', orario_chiusura='10:50',
                       cap=Localita.objects.get(nome_localita='Modena'), via='viale Italia', num_civico=3,
                       telefono='059000000',
                       )
        self.assertEqual(local.orario_apertura < local.orario_chiusura, False)
