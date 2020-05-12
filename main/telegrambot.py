# Example code for telegrambot.py module
import logging
from typing import Optional

from django.conf import settings
from django.template import Template, Context
from django_telegrambot.apps import DjangoTelegramBot
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler

from main.models import Item, TelegramUser, Category, Message

logger = logging.getLogger(__name__)


def chunks(lst, n):
    '''Yield successive n-sized chunks from lst.'''
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def render(template: str, context: Optional[dict] = None):
    return Template(template).render(Context(context))


def show_menu(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(category.name, callback_data=category.get_callback_data()) for category in chunk]
        for chunk in chunks(Category.objects.filter(parent=None), 2)])
    update.effective_message.reply_text(render(Message.get('menu')), reply_markup=keyboard)


def show_submenu(update: Update, context: CallbackContext, category: Category):
    controls = [InlineKeyboardButton('Все категории', callback_data='menu')]
    if category.parent is not None:
        controls = [InlineKeyboardButton('Меню', callback_data=category.parent.get_callback_data())]
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(category.name, callback_data=category.get_callback_data()) for category in chunk]
            for chunk in chunks(category.subcategories.all(), 2)
        ] + [controls])
    update.effective_message.reply_text(render(Message.get('submenu'), {'category': category}),
                                        reply_markup=keyboard)


def show_item(update: Update, context: CallbackContext, item: Item):
    if settings.DEBUG:
        for chunk in chunks(item.covers.all(), 10):
            update.effective_message.reply_media_group([InputMediaPhoto(cover.file.file) for cover in chunk])
    else:
        for chunk in chunks(item.covers.all(), 10):
            update.effective_message.reply_media_group(
                [InputMediaPhoto(settings.WEBSITE_LINK + cover.file.url) for cover in chunk])

    controls = [
        InlineKeyboardButton('Все категории', callback_data='menu')
    ]
    if item.category.parent is not None:
        controls = [InlineKeyboardButton('Назад', callback_data=item.category.parent.get_callback_data())] + controls

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Предыдущий',
                                     callback_data=f'items,{item.category_id},prev,{item.pk}'),
                InlineKeyboardButton('Следующий',
                                     callback_data=f'items,{item.category_id},next,{item.pk}')
            ],
            [
                InlineKeyboardButton('В начало',
                                     callback_data=f'items,{item.category_id},begin'),
                InlineKeyboardButton('В конец',
                                     callback_data=f'items,{item.category_id},end'),
            ]
        ] + [controls])

    update.effective_message.reply_text(render(Message.get('item'), {'item': item}),
                                        reply_markup=keyboard)


def process_callback(update: Update, context: CallbackContext):
    query, *args = update.callback_query.data.split(',')
    if query == 'menu':
        show_menu(update, context)
    elif query == 'items':
        category_id, action, *args = args
        category = Category.objects.get(pk=category_id)

        item = None
        if action == 'begin':
            item = category.items.first()
        elif action == 'end':
            item = category.items.last()
        elif action == 'next':
            item = category.items.filter(pk__gt=int(args[0])).first()
        elif action == 'prev':
            item = category.items.filter(pk__lt=int(args[0])).last()

        if item is not None:
            show_item(update, context, item)
    elif query == 'submenu':
        category_id = args[0]
        category = Category.objects.get(pk=category_id)

        show_submenu(update, context, category)

    update.callback_query.answer()


def start(update: Update, context: CallbackContext):
    TelegramUser.objects.update_or_create(chat_id=update.effective_chat.id,
                                          defaults={
                                              'full_name': update.effective_user.full_name,
                                              'username': update.effective_user.username
                                              if update.effective_user.username is not None else ''
                                          })
    show_menu(update, context)


def get_help(update: Update, context: CallbackContext):
    update.message.reply_text(render(Message.get("help")))


def error(update, context: CallbackContext):
    logger.warn('Update "%s" caused error "%s"' % (update, context.error))


def main():
    logger.info('Loading handlers for telegram bot')

    dp = DjangoTelegramBot.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', get_help))

    dp.add_handler(CallbackQueryHandler(process_callback))

    dp.add_error_handler(error)
