from django.contrib import admin

# Register your models here.
from main.models import Category, Item, Message, TelegramUser, Cover, Entry


class CoverInline(admin.TabularInline):
    model = Cover
    verbose_name = 'Обложка'
    verbose_name_plural = 'Обложки'
    extra = 0


class EntryInline(admin.StackedInline):
    model = Entry
    verbose_name = 'Описание'
    verbose_name_plural = 'Описания'
    extra = 0


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category', 'delivery')
    search_fields = ('item__description',)
    list_filter = ('category',)
    inlines = (CoverInline, EntryInline)
    list_per_page = 25


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'count_items', 'is_super', 'has_models')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'full_name', 'username']
    search_fields = ['full_name', 'username']
