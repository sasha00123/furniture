# Generated by Django 3.0.6 on 2020-06-23 09:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_auto_20200623_0540'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='language',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.MessageLanguage', verbose_name='Язык'),
        ),
    ]