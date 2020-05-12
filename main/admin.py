from django.contrib import admin

# Register your models here.
from main.models import Category, Item, Message, TelegramUser, Cover


class CoverInline(admin.TabularInline):
    model = Cover
    verbose_name = 'Обложка'
    verbose_name_plural = 'Обложки'
    extra = 0


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'price', 'delivery')
    search_fields = ('description',)
    inlines = (CoverInline,)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'count_items', 'is_super')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'full_name', 'username']
    search_fields = ['full_name', 'username']
