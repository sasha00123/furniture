# Generated by Django 3.0.6 on 2020-06-23 00:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_messagelanguage_default'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='messagelanguage',
            options={'verbose_name': 'Язык Сообщений', 'verbose_name_plural': 'Языки Сообщений'},
        ),
        migrations.AlterModelOptions(
            name='messagevalue',
            options={'verbose_name': 'Перевод', 'verbose_name_plural': 'Переводы'},
        ),
    ]
