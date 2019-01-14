from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_utente = models.BooleanField(default=False)
    is_commerciante = models.BooleanField(default=False)
    email = models.EmailField(max_length=50, unique=True)
    via = models.CharField(max_length=255)
    civico = models.CharField(max_length=255)
    cap = models.CharField(max_length=6)
    telefono = models.CharField(max_length=15)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = "Utenti Totali"


class Utente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='utente_user')

    carta_di_credito = models.ManyToManyField("user.CartaDiCredito", blank=True, related_name='carta_di_credito')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Utenti Registrati'


class Commerciante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='commerciante_user')
    p_iva = models.CharField(max_length=11, null=True, unique=True)
    possiede_locale = models.ManyToManyField("localManagement.Locale", blank=True, related_name='possiede_locale')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Commercianti'