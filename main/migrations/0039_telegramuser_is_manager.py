# Generated by Django 3.0.6 on 2020-07-03 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0038_telegramuser_referrer'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='is_manager',
            field=models.BooleanField(default=False, verbose_name='Менеджер'),
        ),
    ]
