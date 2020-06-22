from django.urls import path

from main.views import send_list, get_admins

urlpatterns = [
    path('sendlist', send_list),
    path('admins', get_admins)
]