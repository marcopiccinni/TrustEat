# Generated by Django 2.1.3 on 2018-11-21 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('localManagement', '0003_auto_20181121_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locale',
            name='prezzo_di_spedizione',
            field=models.FloatField(default=0),
        ),
    ]