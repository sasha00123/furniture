# Generated by Django 3.0.6 on 2020-06-25 03:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_auto_20200625_0648'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='description',
        ),
        migrations.CreateModel(
            name='MessageDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='Описание')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_descriptions', to='main.MessageLanguage', verbose_name='Язык')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='descriptions', to='main.Message', verbose_name='Сообщение')),
            ],
        ),
    ]