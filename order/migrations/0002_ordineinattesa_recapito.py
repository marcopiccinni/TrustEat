# Generated by Django 2.1.3 on 2018-11-23 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordineinattesa',
            name='recapito',
            field=models.CharField(max_length=30, null=True),
        ),
    ]