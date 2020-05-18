# Generated by Django 3.0.6 on 2020-05-18 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20200514_0113'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, default='', max_length=255, verbose_name='Описание')),
                ('price', models.PositiveIntegerField(blank=True, default=0, verbose_name='Цена')),
                ('currency', models.CharField(choices=[('сум', 'сум'), ('USD', 'USD')], default='сум', max_length=8, verbose_name='Валюта')),
            ],
        ),
        migrations.RemoveField(
            model_name='item',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='item',
            name='description',
        ),
        migrations.RemoveField(
            model_name='item',
            name='price',
        ),
        migrations.AddField(
            model_name='item',
            name='number',
            field=models.PositiveIntegerField(default=1, verbose_name='Номер'),
            preserve_default=False,
        ),
    ]
