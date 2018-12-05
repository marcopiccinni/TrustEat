from django.db import models
from localManagement.models import Menu, Prodotto, Locale
from user.models import CartaDiCredito
from accounts.models import Utente


class OrdineInAttesa(models.Model):
    CARD = "carta di credito"
    CASH = "alla consegna"

    PAYMENT_CHOICHES = (
        (CARD, 'carta di credito'),
        (CASH, 'alla consegna'),
    )

    cod_ordine = models.AutoField(primary_key=True, serialize=True)
    email = models.ForeignKey(Utente, on_delete=models.DO_NOTHING)
    data = models.DateTimeField(null=False)
    orario_richiesto = models.TimeField(null=False)
    metodo_pagamento = models.CharField(max_length=30, null=False, choices=PAYMENT_CHOICHES)
    cod_carta = models.ForeignKey(CartaDiCredito, on_delete=models.CASCADE, null=True)
    prodotti = models.ManyToManyField(Prodotto, blank=True, through='order.RichiedeP')
    menues = models.ManyToManyField(Menu, blank=True, through='order.RichiedeM')
    accettato = models.BooleanField(default=None, null=True)
    consegnato = models.BooleanField(default=False, null=True)
    descrizione = models.CharField(max_length=200, null=True)

    class Meta:
        unique_together = (('email', 'data'),)
        verbose_name_plural = 'Ordini in Attesa'

    def __str__(self):
        return "Ordine " + str(self.cod_ordine)


class RichiedeM(models.Model):
    cod_ordine = models.ForeignKey(OrdineInAttesa, on_delete=models.CASCADE, null=False)
    cod_locale = models.ForeignKey(Locale, on_delete=models.CASCADE, null=False)
    nome_menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=False, related_name='type_nome_menu_1')
    quantita = models.SmallIntegerField(null=False)

    class Meta:
        unique_together = (('cod_ordine', 'cod_locale', 'nome_menu'),)
        verbose_name_plural = 'Richiede Menù'

    def __str__(self):
        return "Ordine  " + str(self.cod_ordine)


class RichiedeP(models.Model):
    cod_ordine = models.ForeignKey(OrdineInAttesa, on_delete=models.CASCADE, null=False)
    cod_locale = models.ForeignKey(Locale, on_delete=models.CASCADE, null=False)
    nome_prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE, null=False, related_name='type_nome_prodotto')
    quantita = models.SmallIntegerField(null=False)

    class Meta:
        unique_together = (('cod_ordine', 'cod_locale', 'nome_prodotto'),)
        verbose_name_plural = 'Richiede Prodotti'

    def __str__(self):
        return "Ordine  " + str(self.cod_ordine)
