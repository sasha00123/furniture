# Generated by Django 3.0.6 on 2020-05-18 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20200518_1945'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='item',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='main.Item', verbose_name='Товар'),
            preserve_default=False,
        ),
    ]
