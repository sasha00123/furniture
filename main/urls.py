from django.urls import path

from main.views import send_list

urlpatterns = [
    path('sendlist', send_list)
]