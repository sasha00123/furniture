import os
from pathlib import Path

from decouple import config, Csv
from dj_database_url import parse as db_url
from django.template import Template
from functools import partial
import datetime as dt
from django.utils import timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = config('DEBUG', default=False, cast=bool)

SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main.apps.MainConfig',
    'django_telegrambot',
    'django.contrib.humanize'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'furniture_bot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'furniture_bot.wsgi.application'

DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        cast=db_url
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

WEBSITE_LINK = config('WEBSITE_LINK', default='http://localhost:8000')

USE_WEBHOOK = config('USE_WEBHOOK', cast=bool)

if USE_WEBHOOK:
    DJANGO_TELEGRAMBOT = {
        'MODE': 'WEBHOOK',
        'WEBHOOK_SITE': WEBSITE_LINK,
        'BOTS': [
            {
                'MESSAGEQUEUE_ENABLED': True,
                'TOKEN': config('TELEGRAM_BOT_TOKEN'),
            },
        ],

    }
else:
    DJANGO_TELEGRAMBOT = {
        'MODE': 'POLLING',
        'BOTS': [
            {
                'MESSAGEQUEUE_ENABLED': True,
                'TOKEN': config('TELEGRAM_BOT_TOKEN'),
            },
        ],

    }

LAUNCH_DATE = timezone.make_aware(
    config('LAUNCH_DATE', dt.datetime(2020, 6, 20), cast=lambda date: dt.datetime.strptime(date, "%d.%m.%Y")))
