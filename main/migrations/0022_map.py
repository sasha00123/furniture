# Generated by Django 3.0.6 on 2020-06-15 05:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20200615_1017'),
    ]

    operations = [
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.FloatField(verbose_name='Широта')),
                ('long', models.FloatField(verbose_name='Долгота')),
                ('info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='maps', to='main.InfoButton')),
            ],
        ),
    ]