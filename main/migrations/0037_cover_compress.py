# Generated by Django 3.0.6 on 2020-07-01 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_auto_20200625_0817'),
    ]

    operations = [
        migrations.AddField(
            model_name='cover',
            name='compress',
            field=models.BooleanField(default=True, verbose_name='Сжатие'),
        ),
    ]