from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from localManagement.models import Locale
from accounts.models import Utente, Commerciante
import datetime


class CartaDiCredito(models.Model):
    cod_carta = models.AutoField(primary_key=True, serialize=True)
    numero_carta = models.CharField(max_length=16, null=False, unique=True)
    intestatario = models.CharField(max_length=60, null=False)
    scadenza = models.DateField(null=False)

    class Meta:
        verbose_name_plural = 'Carte di credito'

    def __str__(self):
        return self.numero_carta

    def is_valid(self):
        if self.scadenza.year >= datetime.datetime.now().year and self.scadenza.month >= datetime.datetime.now().month:
            return True
        else:
            return False


class Recensione(models.Model):
    cod_recensione = models.AutoField(primary_key=True, serialize=True)
    email = models.ForeignKey(Utente, on_delete=models.CASCADE, null=False)
    cod_locale = models.ForeignKey(Locale, on_delete=models.CASCADE, null=False)
    p_iva = models.ForeignKey(Commerciante, on_delete=models.CASCADE, null=True, blank=True)
    voto = models.SmallIntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    descrizione = models.CharField(max_length=130, null=True)
    date = models.DateField(null=False)

    class Meta:
        unique_together = (('email', 'cod_locale', 'p_iva'),)
        verbose_name_plural = 'Recensioni'

    def __str__(self):
        return str(self.email.user.username)
