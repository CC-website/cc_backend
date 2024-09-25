# messaging/urls.py

from django.urls import path

from messaging.views import MessageListCreateView, exchange_keys, fetch_messages, send_message

urlpatterns = [
    path('messages/', MessageListCreateView.as_view(), name='message-create'),
    path('messages/exchange_keys/', exchange_keys, name='exchange_keys'),
    path('messages/send_message/', send_message, name='send_message'),
    path('messages/fetch_messages/', fetch_messages, name='fetch_messages'),
]