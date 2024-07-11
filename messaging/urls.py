# messaging/urls.py

from django.urls import path

from messaging.views import MessageListCreateView

urlpatterns = [
    path('messages/', MessageListCreateView.as_view(), name='message-create'),
]