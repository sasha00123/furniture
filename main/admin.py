from django.contrib import admin

# Register your models here.
from main.models import Category, Item, Message


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'price', 'delivery')
    search_fields = ('description',)


class ItemInline(admin.TabularInline):
    model = Item
    verbose_name = 'Товар'
    verbose_name_plural = 'Товары'
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (ItemInline,)
    list_display = ('name', 'count_items', 'is_super')

    def save_model(self, request, obj: Category, form, change):
        obj.save()

        for afile in request.FILES.getlist('photos_multiple'):
            obj.items.create(cover=afile)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
