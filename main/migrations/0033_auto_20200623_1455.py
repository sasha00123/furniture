# Generated by Django 3.0.6 on 2020-06-23 09:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_auto_20200623_1428'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='name',
        ),
        migrations.RemoveField(
            model_name='infobutton',
            name='name',
        ),
        migrations.AlterField(
            model_name='entry',
            name='language',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='main.MessageLanguage', verbose_name='Язык'),
        ),
        migrations.AlterField(
            model_name='infobuttondescription',
            name='language',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='descriptions', to='main.MessageLanguage', verbose_name='Язык'),
        ),
        migrations.CreateModel(
            name='InfoButtonName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=255, verbose_name='Заголовок')),
                ('button', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='names', to='main.InfoButton', verbose_name='Кнопка')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='info_button_names', to='main.MessageLanguage', verbose_name='Язык')),
            ],
            options={
                'verbose_name': 'Заголовок',
                'verbose_name_plural': 'Заголовки',
            },
        ),
        migrations.CreateModel(
            name='CategoryName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=255, verbose_name='Заголовок')),
                ('button', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='names', to='main.Category', verbose_name='Кнопка')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_names', to='main.MessageLanguage', verbose_name='Язык')),
            ],
            options={
                'verbose_name': 'Заголовок',
                'verbose_name_plural': 'Заголовки',
            },
        ),
    ]
