from django.contrib import admin

# Register your models here.
from main.models import Category, Item, Message, TelegramUser, Cover, Entry, InfoButton, Map, MessageValue, \
    MessageLanguage, InfoButtonDescription, InfoButtonName, CategoryName, MessageDescription


class InfoCoverInline(admin.TabularInline):
    model = Cover
    verbose_name = 'Обложка'
    verbose_name_plural = 'Обложки'
    exclude = ("item",)
    extra = 0


class MapInline(admin.TabularInline):
    model = Map
    verbose_name = "Карта"
    verbose_name_plural = "Карты"
    extra = 0


class ItemCoverInline(admin.TabularInline):
    model = Cover
    verbose_name = 'Обложка'
    verbose_name_plural = 'Обложки'
    exclude = ("info",)
    extra = 0


class EntryInline(admin.StackedInline):
    model = Entry
    verbose_name = 'Описание'
    verbose_name_plural = 'Описания'
    extra = 0


class InfoButtonNameInline(admin.StackedInline):
    model = InfoButtonName
    verbose_name = 'Заголовок'
    verbose_name_plural = 'Заголовки'
    extra = 0


class InfoButtonDescriptionInline(admin.StackedInline):
    model = InfoButtonDescription
    verbose_name = 'Перевод'
    verbose_name_plural = 'Переводы'
    extra = 0


class CategoryNameInline(admin.StackedInline):
    model = CategoryName
    verbose_name = 'Заголовок'
    verbose_name_plural = 'Заголовки'
    extra = 0


@admin.register(InfoButton)
class InfoButtonAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    search_fields = ('__str__',)
    inlines = (InfoButtonNameInline, InfoButtonDescriptionInline, InfoCoverInline, MapInline)
    list_per_page = 25


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category', 'delivery')
    search_fields = ('item__description',)
    list_filter = ('category',)
    inlines = (ItemCoverInline, EntryInline)
    list_per_page = 25


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'count_items', 'is_super', 'has_models')
    inlines = [CategoryNameInline]


class MessageValueInline(admin.StackedInline):
    model = MessageValue
    verbose_name = 'Перевод'
    verbose_name_plural = 'Переводы'
    extra = 0


class MessageDescriptionInline(admin.StackedInline):
    model = MessageDescription
    verbose_name = 'Описание'
    verbose_name_plural = 'Описания'
    extra = 0


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [MessageDescriptionInline, MessageValueInline]


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'full_name', 'real_name', 'username', 'phone', 'referrer', 'is_admin', 'is_manager']
    search_fields = ['full_name', 'username']


@admin.register(MessageLanguage)
class MessageLanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'default']
    search_fields = ['name']
