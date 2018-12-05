from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
import os


# Create your models here.

class Localita(models.Model):
    cap = models.CharField(max_length=5, primary_key=True)
    nome_localita = models.CharField(max_length=50, null=False, unique=True)

    def __str__(self):
        return self.nome_localita

    class Meta:
        verbose_name_plural = 'Località'
        verbose_name = 'Località'


class Tag(models.Model):
    nome_tag = models.CharField(primary_key=True, max_length=20)

    def __str__(self):
        return self.nome_tag


class Locale(models.Model):
    cod_locale = models.AutoField(primary_key=True, serialize=True)
    nome_locale = models.CharField(max_length=30, null=False)
    orario_apertura = models.TimeField(null=False)
    orario_chiusura = models.TimeField(null=False)
    num_civico = models.CharField(max_length=10, null=False)
    via = models.CharField(max_length=50, null=False)
    cap = models.ForeignKey(Localita, on_delete=models.CASCADE)
    descrizione = models.CharField(max_length=200, null=True)
    telefono = models.CharField(max_length=15, null=False)
    sito_web = models.CharField(max_length=50, null=True)
    prezzo_di_spedizione = models.FloatField(null=False, default=0)
    email = models.EmailField(null=True)
    tag = models.ManyToManyField(Tag, blank=True, related_name='locale_tag')

    class Meta:
        unique_together = (("nome_locale", "cap"),)
        verbose_name_plural = 'Locali'

    def __str__(self):
        return self.nome_locale


def validate_image_size(value):
    image_size = value.size

    if image_size > 10485760:
        raise ValidationError("La dimensione massima della foto per poter essere "
                              "uplodata e' di 10 MB")
    else:
        return value


def local_images_path(instance, filename):
    name, ext = filename.rsplit('.', 1)
    dt = datetime.now()
    file_path = 'media_db/{cod_locale_id}/locale/'.format(cod_locale_id=instance.cod_locale_id)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_path = '{cod_locale_id}/locale/{date}.{ext}'.format(cod_locale_id=instance.cod_locale_id, date=dt, ext=ext)
    return file_path


class FotoLocale(models.Model):
    cod_locale = models.ForeignKey(Locale, on_delete=models.CASCADE)
    foto_locale = models.ImageField(upload_to=local_images_path, blank=True, null=True,
                                    validators=[validate_image_size])

    class Meta:
        verbose_name_plural = 'Foto Locali'

    def __str__(self):
        return self.cod_locale.nome_locale


class Chiusura(models.Model):
    cod_locale = models.ForeignKey(Locale, on_delete=models.CASCADE)
    CHOICES = [
        ('Lunedì', 'Lunedì'),
        ('Martedì', 'Martedì'),
        ('Mercoledì', 'Mercoledì'),
        ('Giovedì', 'Giovedì'),
        ('Venerdì', 'Venerdì'),
        ('Sabato', 'Sabato'),
        ('Domenica', 'Domenica'),
    ]
    giorno_chiusura = models.CharField(max_length=10, null=True, choices=CHOICES)

    class Meta:
        unique_together = (("cod_locale", "giorno_chiusura"),)
        verbose_name_plural = verbose_name = 'Chiusura'

    def __str__(self):
        return self.cod_locale.nome_locale


class Tipo(models.Model):
    nome_tipo = models.CharField(max_length=20, primary_key=True)

    class Meta:
        verbose_name_plural = 'Tipi'

    def __str__(self):
        return self.nome_tipo


class Menu(models.Model):
    cod_locale = models.ForeignKey(Locale, on_delete=models.CASCADE)
    nome_menu = models.CharField(max_length=30, null=False)
    descrizione_menu = models.CharField(max_length=200, null=False)
    prezzo = models.DecimalField(decimal_places=2, max_digits=4)
    composto_da_prodotti = models.ManyToManyField("localManagement.Prodotto", blank=True,
                                                  related_name='composto_da_prodotti',
                                                  through='localManagement.CompostoDa')

    class Meta:
        unique_together = (("cod_locale", "nome_menu"),)
        verbose_name_plural = verbose_name = 'Menù'

    def __str__(self):
        return self.nome_menu


def product_images_path(instance, filename):
    name, ext = filename.rsplit('.', 1)
    dt = datetime.now()
    file_path = 'media_db/{cod_locale_id}/{nome_prodotto}/'.format(cod_locale_id=instance.cod_locale_id,
                                                                   nome_prodotto=instance.nome_prodotto,
                                                                   )
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_path = '{cod_locale_id}/{nome_prodotto}/{date}.{ext}'.format(cod_locale_id=instance.cod_locale_id,
                                                                      nome_prodotto=instance.nome_prodotto,
                                                                      date=dt, ext=ext,
                                                                      )
    return file_path


class Prodotto(models.Model):
    cod_locale = models.ForeignKey(Locale, on_delete=models.CASCADE, null=False)
    nome_prodotto = models.CharField(max_length=30, null=False)
    descrizione_prodotto = models.CharField(max_length=200, null=False)
    prezzo = models.DecimalField(decimal_places=2, max_digits=4)
    nome_tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)
    foto_prodotto = models.ImageField(upload_to=product_images_path, null=True, blank=True,
                                      validators=[validate_image_size])

    class Meta:
        unique_together = (("cod_locale", "nome_prodotto"),)
        verbose_name_plural = 'Prodotti'

    def __str__(self):
        return self.nome_prodotto


class CompostoDa(models.Model):
    cod_locale = models.ForeignKey(Locale, on_delete=models.CASCADE, null=False)
    nome_menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=False, related_name='type_nome_menu')
    nome_prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE, null=False)

    class Meta:
        unique_together = (("cod_locale", "nome_menu", "nome_prodotto"),)
        verbose_name_plural = verbose_name = 'Composto da'

    def __str__(self):
        return self.cod_locale.nome_locale
