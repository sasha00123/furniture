import uuid
from io import BytesIO
import os
from functools import partial

from PIL import Image
from django.db import models

import logging


class MessageLanguage(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название", db_index=True, unique=True)
    default = models.BooleanField(verbose_name='По умолчанию?', db_index=True, default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Язык Сообщений'
        verbose_name_plural = 'Языки Сообщений'


class MenuButton(models.Model):
    priority = models.IntegerField(default=0, blank=True, verbose_name='Приоритет')

    def get_name(self, language):
        raise NotImplementedError

    def get_callback_data(self):
        raise NotImplementedError

    class Meta:
        abstract = True


class InfoButton(MenuButton):
    def get_callback_data(self):
        return f"info,{self.id}"

    def get_name(self, language):
        if language is None:
            language = MessageLanguage.objects.get(default=True)
        try:
            return self.names.get(language=language).name
        except InfoButtonName.DoesNotExist:
            language = MessageLanguage.objects.get(default=True)
            return self.names.get(language=language).name

    def get_description(self, language):
        if language is None:
            language = MessageLanguage.objects.get(default=True)
        try:
            return self.descriptions.get(language=language).description
        except InfoButtonDescription.DoesNotExist:
            language = MessageLanguage.objects.get(default=True)
            return self.descriptions.get(language=language).description

    def __str__(self):
        return ', '.join([name.name for name in self.names.all()])

    class Meta:
        verbose_name = 'Информационная кнопка'
        verbose_name_plural = 'Информационные кнопки'


class InfoButtonName(models.Model):
    language = models.ForeignKey(MessageLanguage, on_delete=models.CASCADE, related_name='info_button_names',
                                 verbose_name='Язык')
    name = models.CharField(max_length=255, blank=True, default="", verbose_name='Заголовок')
    button = models.ForeignKey(InfoButton, on_delete=models.CASCADE, related_name='names', verbose_name='Кнопка')

    class Meta:
        verbose_name = 'Заголовок'
        verbose_name_plural = 'Заголовки'


class InfoButtonDescription(models.Model):
    language = models.ForeignKey(MessageLanguage, on_delete=models.CASCADE, related_name='descriptions',
                                 verbose_name='Язык', null=True)
    description = models.TextField(blank=True, default="", verbose_name='Описание')
    button = models.ForeignKey(InfoButton, on_delete=models.CASCADE, related_name='descriptions', verbose_name='Кнопка')

    class Meta:
        verbose_name = 'Перевод'
        verbose_name_plural = 'Переводы'


class Map(models.Model):
    lat = models.FloatField(verbose_name='Широта')
    long = models.FloatField(verbose_name='Долгота')

    info = models.ForeignKey(InfoButton, on_delete=models.CASCADE, related_name='maps')


class Category(MenuButton):
    has_models = models.BooleanField(verbose_name="Разбиение на модели?")

    parent = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='subcategories',
                               verbose_name='Основная категория', blank=True, null=True)

    def count_items(self):
        return self.items.count() if not self.is_super() else sum(
            [category.count_items() for category in self.subcategories.all()]
        )

    count_items.short_description = "Количество товаров"

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return ', '.join([name.name for name in self.names.all()])

    def is_super(self):
        return self.subcategories.count() > 0

    def get_name(self, language):
        if language is None:
            language = MessageLanguage.objects.get(default=True)
        try:
            return self.names.get(language=language).name
        except CategoryName.DoesNotExist:
            language = MessageLanguage.objects.get(default=True)
            return self.names.get(language=language).name

    is_super.boolean = True
    is_super.short_description = "Имеет подкатегории?"

    def get_callback_data(self):
        if self.is_super():
            return f"submenu,{self.id}"
        if self.has_models:
            return f"items,{self.id},list"
        return f"items,{self.id},begin"


class CategoryName(models.Model):
    language = models.ForeignKey(MessageLanguage, on_delete=models.CASCADE, related_name='category_names',
                                 verbose_name='Язык')
    name = models.CharField(max_length=255, blank=True, default="", verbose_name='Заголовок')
    button = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='names', verbose_name='Кнопка')

    class Meta:
        verbose_name = 'Заголовок'
        verbose_name_plural = 'Заголовки'


class Item(models.Model):
    number = models.PositiveIntegerField(verbose_name='Номер', blank=True, null=True,
                                         help_text='Не нужно указывать, если это не модель.')

    delivery = models.BooleanField(default=False, verbose_name='Доставка')

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items", verbose_name='Категория')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        if self.number is not None:
            return f"Модель ({self.number})"

        result = '|'.join((entry.description for entry in self.entries.all()))
        return result if result else "Без названия"

    def get_entries(self, language):
        if language is None:
            language = MessageLanguage.objects.get(default=True)
        return self.entries.filter(language=language)


class Entry(models.Model):
    CURRENCY_CHOICES = [
        ('сум', 'сум'),
        ('USD', 'USD')
    ]

    language = models.ForeignKey(MessageLanguage, on_delete=models.CASCADE,
                                 related_name='entries', verbose_name="Язык",
                                 null=True)
    description = models.CharField(max_length=255, blank=True, default="", verbose_name='Заголовок')
    long_description = models.TextField(blank=True, default="", verbose_name='Описание')
    price = models.PositiveIntegerField(blank=True, default=0, verbose_name='Цена')
    currency = models.CharField(max_length=8, choices=CURRENCY_CHOICES, default='сум', verbose_name='Валюта')
    show_price = models.BooleanField(default=True, verbose_name='Показывать цену')

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='entries', verbose_name='Товар')

    def __str__(self):
        return self.description


class Message(models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    @staticmethod
    def get(name, language):
        if language is None:
            language = MessageLanguage.objects.get(default=True)
        try:
            return Message.objects.get(name=name).values.get(language=language).text
        except MessageValue.DoesNotExist:
            language = MessageLanguage.objects.get(default=True)
            return Message.objects.get(name=name).values.get(language=language).text

    def __str__(self):
        return self.name


class MessageDescription(models.Model):
    description = models.CharField(max_length=255, blank=True, verbose_name='Описание')
    language = models.ForeignKey(MessageLanguage, on_delete=models.CASCADE, related_name='message_descriptions',
                                 verbose_name='Язык')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='descriptions',
                                verbose_name='Сообщение')


class MessageValue(models.Model):
    text = models.TextField(verbose_name="Текст")
    language = models.ForeignKey(MessageLanguage, on_delete=models.CASCADE, related_name='messages',
                                 verbose_name='Язык')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='values', verbose_name='Сообщение')

    class Meta:
        verbose_name = 'Перевод'
        verbose_name_plural = 'Переводы'


class TelegramUser(models.Model):
    chat_id = models.BigIntegerField(db_index=True, verbose_name='ID чата', unique=True)
    full_name = models.CharField(max_length=255, verbose_name='Имя Telegram')
    real_name = models.CharField(max_length=255, verbose_name='Полное имя', default="")
    username = models.CharField(max_length=255, blank=True, verbose_name='Username')
    is_admin = models.BooleanField(default=False, verbose_name='Администратор')
    is_manager = models.BooleanField(default=False, verbose_name='Менеджер')
    joined = models.DateTimeField(auto_now_add=True, verbose_name='Зарегистрирован')

    language = models.ForeignKey(MessageLanguage, on_delete=models.CASCADE,
                                 related_name='users', verbose_name='Язык',
                                 null=True)
    phone = models.CharField(max_length=63, verbose_name='Телефон', null=True)

    referrer = models.ForeignKey("TelegramUser", on_delete=models.CASCADE, related_name="referrals",
                                 verbose_name='Реферер', null=True)

    class Meta:
        verbose_name = 'Пользователь Telegram'
        verbose_name_plural = 'Пользователи Telegram'

    def __str__(self):
        return self.full_name


def unique_filename(folder, instance, filename):
    _, ext = os.path.splitext(filename)
    generated_name = f"{uuid.uuid4()}{ext}"
    return os.path.join(folder, generated_name)


class Cover(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='covers', blank=True, null=True)
    info = models.ForeignKey(InfoButton, on_delete=models.CASCADE, related_name='covers', blank=True, null=True)

    file = models.ImageField(upload_to=partial(unique_filename, 'covers'), verbose_name='Обложка', max_length=255)
    compress = models.BooleanField(default=True, verbose_name='Сжатие')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.file:
            with Image.open(self.file) as img:
                if self.compress:
                    img.thumbnail((640, 640), Image.ANTIALIAS)
                img.save(self.file.path)
