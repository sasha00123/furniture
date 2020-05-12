from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
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
        return self.name

    def is_super(self):
        return self.subcategories.count() > 0

    is_super.boolean = True
    is_super.short_description = "Имеет подкатегории?"

    def get_callback_data(self):
        if self.is_super():
            return f"submenu,{self.id}"
        if self.has_models:
            return f"items,{self.id},list"
        return f"items,{self.id},begin"


class Item(models.Model):
    description = models.CharField(max_length=255, blank=True, default="", verbose_name='Описание')
    price = models.PositiveIntegerField(blank=True, default=0, verbose_name='Цена')
    delivery = models.BooleanField(default=False, verbose_name='Доставка')

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items", verbose_name='Категория')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.description if self.description else "Без названия"


class TelegramUser(models.Model):
    chat_id = models.BigIntegerField(db_index=True, verbose_name='ID чата')
    full_name = models.CharField(max_length=255, verbose_name='Полное имя')
    username = models.CharField(max_length=255, blank=True, verbose_name='Username')

    class Meta:
        verbose_name = 'Пользователь Telegram'
        verbose_name_plural = 'Пользователи Telegram'

    def __str__(self):
        return self.full_name


class Message(models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    description = models.CharField(max_length=255, blank=True)
    value = models.TextField()

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    @staticmethod
    def get(name):
        return Message.objects.get(name=name).value

    def __str__(self):
        return self.name


class Cover(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='covers')
    file = models.ImageField(upload_to='covers/', verbose_name='Обложка')
