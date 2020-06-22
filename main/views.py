from django.http import HttpResponse
from django.shortcuts import render
import json

from main.models import TelegramUser


def send_list(request):
    return HttpResponse(json.dumps([{"Telegram ID": user.chat_id} for user in TelegramUser.objects.all()]))


def get_admins(request):
    return HttpResponse(json.dumps([user.chat_id for user in TelegramUser.objects.filter(is_admin=True)]))
