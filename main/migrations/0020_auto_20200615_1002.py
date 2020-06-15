# Generated by Django 3.0.6 on 2020-06-15 05:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_entry_show_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfoButton',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', max_length=255, verbose_name='Заголовок')),
                ('description', models.TextField(blank=True, default='', verbose_name='Описание')),
            ],
        ),
        migrations.AlterField(
            model_name='cover',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='covers', to='main.Item'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='show_price',
            field=models.BooleanField(default=True, verbose_name='Показывать цену'),
        ),
        migrations.AddField(
            model_name='cover',
            name='info',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='covers', to='main.InfoButton'),
        ),
    ]
