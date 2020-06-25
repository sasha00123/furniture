import logging
from typing import Optional

from django.conf import settings
from django.template import Template, Context
from django.utils import timezone
from django.utils.timezone import now
from django_telegrambot.apps import DjangoTelegramBot
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, ParseMode, \
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, ConversationHandler, MessageHandler, \
    Filters
from telegram.ext.dispatcher import run_async
from itertools import chain
import datetime as dt

from main.models import Item, TelegramUser, Category, Message, InfoButton, MessageLanguage

logger = logging.getLogger(__name__)

LANGUAGE, FULL_NAME, PHONE = list(range(3))


def inject_user(func):
    def injection_func(update: Update, context: CallbackContext, *args, **kwargs):
        user, _ = TelegramUser.objects.update_or_create(chat_id=update.effective_chat.id,
                                                        defaults={
                                                            'full_name': update.effective_user.full_name,
                                                            'username': update.effective_user.username
                                                            if update.effective_user.username is not None else ''
                                                        })
        return func(update, context, *args, user=user, **kwargs)

    return injection_func


def is_admin(func):
    @inject_user
    def authorized_request(update: Update, context: CallbackContext, user: TelegramUser, *args, **kwargs):
        if not user.is_admin:
            update.effective_message.reply_text(render(Message.get("admin_access_required", user.language)))
        else:
            return func(update, context, *args, **kwargs)

    return authorized_request


class KeyboardEntryPoint:
    def __init__(self, message):
        self.messsage = message

    def __contains__(self, item):
        for lang in MessageLanguage.objects.all():
            if item in Message.get(self.messsage, lang):
                return True
        return False

    def __eq__(self, item):
        for lang in MessageLanguage.objects.all():
            if item == Message.get(self.messsage, lang):
                return True
        return False


@inject_user
def get_main_keyboard(update: Update, context: CallbackContext, user: TelegramUser):
    return ReplyKeyboardMarkup([
        [Message.get(control, user.language)] for control in
        ("change_language_button", "change_full_name_button", "main_menu_button")
    ], one_time_keyboard=True, resize_keyboard=True)


def show_covers(update: Update, context: CallbackContext, covers):
    if settings.DEBUG:
        for chunk in chunks(covers, 10):
            update.effective_message.reply_media_group([InputMediaPhoto(cover.file.file) for cover in chunk])
    else:
        for chunk in chunks(covers, 10):
            update.effective_message.reply_media_group(
                [InputMediaPhoto(settings.WEBSITE_LINK + cover.file.url) for cover in chunk])


def send_maps(update: Update, context: CallbackContext, maps):
    for mp in maps:
        update.effective_message.reply_location(mp.lat, mp.long)


def chunks(lst, n):
    '''Yield successive n-sized chunks from lst.'''
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def render(template: str, context: Optional[dict] = None):
    return Template(template).render(Context(context))


@inject_user
def show_info(update: Update, context: CallbackContext, info: InfoButton, user: TelegramUser):
    send_maps(update, context, info.maps.all())
    show_covers(update, context, info.covers.all())

    controls = [[InlineKeyboardButton(render(Message.get("all_categories", user.language)), callback_data='menu')]]

    keyboard = InlineKeyboardMarkup(controls)

    update.effective_message.reply_text(
        render(Message.get('info', user.language), {
            'info': info,
            'info_name': info.get_name(user.language),
            'info_description': info.get_description(user.language)
        }),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML)


@inject_user
def show_menu(update: Update, context: CallbackContext, user: TelegramUser):
    buttons = [InlineKeyboardButton(obj.get_name(user.language), callback_data=obj.get_callback_data()) for obj in
               sorted(chain(
                   Category.objects.filter(parent=None), InfoButton.objects.all()
               ), key=lambda x: x.priority, reverse=True)]

    keyboard = InlineKeyboardMarkup([chunk for chunk in chunks(buttons, 2)])

    update.effective_message.reply_text(render(Message.get("menu_begin", user.language)),
                                        reply_markup=get_main_keyboard(update, context))
    update.effective_message.reply_text(render(Message.get('menu', user.language)),
                                        reply_markup=keyboard,
                                        parse_mode=ParseMode.HTML)


@inject_user
def show_submenu(update: Update, context: CallbackContext, category: Category, user: TelegramUser):
    controls = [InlineKeyboardButton('Все категории', callback_data='menu')]
    if category.parent is not None:
        controls = [InlineKeyboardButton('Назад', callback_data=category.parent.get_callback_data())]
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(category.get_name(user.language), callback_data=category.get_callback_data()) for
             category in chunk]
            for chunk in chunks(category.subcategories.order_by('-priority'), 2)
        ] + [controls])
    update.effective_message.reply_text(render(Message.get('submenu', user.language),
                                               {'category': category,
                                                'category_name': category.get_name(user.language)}),
                                        reply_markup=keyboard,
                                        parse_mode=ParseMode.HTML)


@inject_user
def show_category_list(update: Update, context: CallbackContext, category: Category, user: TelegramUser):
    controls = [InlineKeyboardButton('Все категории', callback_data='menu')]
    if category.parent is not None:
        controls = [InlineKeyboardButton('Назад', callback_data=category.parent.get_callback_data())]
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(f'Модель {i}', callback_data=f"items,{item.category_id},get,{item.pk}")
          for i, item in chunk]
         for chunk in chunks(list(enumerate(category.items.order_by('pk'), 1)), 2)]
        + [controls])
    update.effective_message.reply_text(render(Message.get('submenu', user.language),
                                               {
                                                   'category': category,
                                                   'category_name': category.get_name(user.language)
                                               }),
                                        reply_markup=keyboard,
                                        parse_mode=ParseMode.HTML)


@inject_user
def show_item(update: Update, context: CallbackContext, item: Item, user: TelegramUser):
    show_covers(update, context, item.covers.all())

    controls = [
        InlineKeyboardButton('Все категории', callback_data='menu')
    ]

    if item.category.has_models:
        controls = [InlineKeyboardButton('Назад', callback_data=item.category.get_callback_data())] + controls
    elif item.category.parent is not None:
        controls = [InlineKeyboardButton('Назад', callback_data=item.category.parent.get_callback_data())] + controls

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Предыдущий',
                                     callback_data=f'items,{item.category_id},prev,{item.pk}'),
                InlineKeyboardButton('Следующий',
                                     callback_data=f'items,{item.category_id},next,{item.pk}')
            ]
        ] + [controls])

    update.effective_message.reply_text(
        render(Message.get('item', user.language), {'item': item, 'entries': item.get_entries(user.language)}),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML)


@run_async
def process_callback(update: Update, context: CallbackContext):
    query, *args = update.callback_query.data.split(',')
    if query == 'menu':
        show_menu(update, context)
    elif query == 'items':
        category_id, action, *args = args
        category = Category.objects.get(pk=category_id)

        if action == 'list':
            show_category_list(update, context, category)
        else:
            item = None
            if action == 'get':
                item = category.items.get(pk=args[0])
            elif action == "begin":
                item = category.items.first()
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
    elif query == "info":
        info_id = args[0]
        info = InfoButton.objects.get(pk=info_id)

        show_info(update, context, info)

    update.callback_query.answer()


@inject_user
def ask_language(update: Update, context: Context, user: TelegramUser):
    buttons = [language.name for language in MessageLanguage.objects.all()]
    keyboard = ReplyKeyboardMarkup([chunk for chunk in chunks(buttons, 2)], resize_keyboard=True)
    update.message.reply_text(render(Message.get("language", MessageLanguage.objects.get(default=True))),
                              reply_markup=keyboard)
    return LANGUAGE


@inject_user
def ask_phone(update: Update, context: CallbackContext, user: TelegramUser):
    # Asking for phone
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(render(Message.get("phone_button", user.language)), request_contact=True)]],
        resize_keyboard=True)
    update.message.reply_text(Message.get("phone", user.language), reply_markup=keyboard)
    return PHONE


@inject_user
def ask_full_name(update: Update, context: CallbackContext, user: TelegramUser):
    update.message.reply_text(render(Message.get("full_name", user.language)), reply_markup=ReplyKeyboardRemove())
    return FULL_NAME


@inject_user
def start(update: Update, context: CallbackContext, user: TelegramUser):
    if user.language is None:
        return ask_language(update, context)
    if not user.real_name:
        return ask_full_name(update, context)
    if user.phone is None:
        return ask_phone(update, context)

    show_menu(update, context)
    return ConversationHandler.END


@run_async
@inject_user
def get_help(update: Update, context: CallbackContext, user: TelegramUser):
    update.message.reply_text(render(Message.get("help", user.language)),
                              parse_mode=ParseMode.HTML)


@run_async
@is_admin
@inject_user
def get_stats(update: Update, context: CallbackContext, user: TelegramUser):
    update.effective_message.reply_text(render(Message.get("stats", user.language), {
        'days': (now() - settings.LAUNCH_DATE).days,
        'total_users': TelegramUser.objects.count(),
        'new_users_today': TelegramUser.objects.filter(joined__gte=timezone.now() - dt.timedelta(days=1)).count()
    }))


@inject_user
def process_language(update: Update, context: CallbackContext, user: TelegramUser):
    try:
        language = MessageLanguage.objects.get(name=update.message.text)
    except MessageLanguage.DoesNotExist:
        update.message.reply_text(Message.get("wrong_language", user.language))
        return False

    # Saving
    user.language = language
    user.save()

    return True


@inject_user
def process_full_name(update: Update, context: CallbackContext, user: TelegramUser):
    user.real_name = update.message.text
    user.save()


def update_full_name(update: Update, context: CallbackContext):
    process_full_name(update, context)

    show_menu(update, context)

    return ConversationHandler.END


def set_full_name(update: Update, context: CallbackContext):
    process_full_name(update, context)

    ask_phone(update, context)

    return PHONE


def update_language(update: Update, context: CallbackContext):
    ok = process_language(update, context)
    if not ok:
        return LANGUAGE

    show_menu(update, context)

    return ConversationHandler.END


def set_language(update: Update, context: CallbackContext):
    ok = process_language(update, context)
    if not ok:
        return LANGUAGE

    ask_full_name(update, context)
    return FULL_NAME


@inject_user
def set_phone(update: Update, context: CallbackContext, user: TelegramUser):
    if update.message.contact.user_id != update.message.chat_id:
        update.message.reply_text(render(Message.get("wrong_phone", user.language)))
        return PHONE

    user.phone = update.message.contact.phone_number
    user.save()

    show_menu(update, context)

    return ConversationHandler.END


@run_async
def error(update: Update, context: CallbackContext):
    s = 'Update "%s" caused error "%s"' % (update, context.error)
    logger.warning(s)
    if settings.ADMIN_CHAT_ID:
        context.bot.send_message(settings.ADMIN_CHAT_ID, s)


def main():
    logger.info('Loading handlers for telegram bot')

    dp = DjangoTelegramBot.dispatcher

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      MessageHandler(Filters.text([KeyboardEntryPoint("main_menu_button")]), start)],
        states={
            LANGUAGE: [MessageHandler(Filters.text & ~Filters.command, set_language)],
            FULL_NAME: [MessageHandler(Filters.text & ~Filters.command, set_full_name)],
            PHONE: [MessageHandler(Filters.contact, set_phone)]
        },
        fallbacks=[],
        name="InitialConversation",
        persistent=True,
        allow_reentry=True
    ))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('lang', ask_language),
                      MessageHandler(Filters.text([KeyboardEntryPoint("change_language_button")]), ask_language)],
        states={
            LANGUAGE: [MessageHandler(Filters.text & ~Filters.command, update_language)],
        },
        fallbacks=[CommandHandler('cancel', show_menu)],
        name="UpdateLanguage",
        persistent=True,
        allow_reentry=True
    ))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('fio', ask_full_name),
                      MessageHandler(Filters.text([KeyboardEntryPoint("change_full_name_button")]), ask_full_name)],
        states={
            FULL_NAME: [MessageHandler(Filters.text & ~Filters.command, update_full_name)],
        },
        fallbacks=[CommandHandler('cancel', show_menu)],
        name="UpdateFullName",
        persistent=True,
        allow_reentry=True
    ))

    dp.add_handler(CommandHandler('help', get_help))
    dp.add_handler(CommandHandler('stats', get_stats))

    dp.add_handler(CallbackQueryHandler(process_callback))

    dp.add_error_handler(error)
