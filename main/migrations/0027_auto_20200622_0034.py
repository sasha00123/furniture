# Generated by Django 3.0.6 on 2020-06-21 19:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_telegramuser_is_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='joined',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Зарегистрирован'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='is_admin',
            field=models.BooleanField(default=False, verbose_name='Администратор'),
        ),
    ]
