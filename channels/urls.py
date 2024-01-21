# urls.py

from django.urls import path
from .views import ChannelView, SubChannelView, GroupView

urlpatterns = [
    path('channels/', ChannelView.as_view(), name='channel-list'),
    path('channels/<int:channel_id>/', ChannelView.as_view(), name='channel-detail'),
    path('channels/delete/<int:channel_id>/', ChannelView.as_view(), name='channel-delete'),
    path('subchannels/', SubChannelView.as_view(), name='subchannel-list'),
    path('subchannels/<int:subchannel_id>/', SubChannelView.as_view(), name='subchannel-detail'),
    path('subchannels/delete/<int:subchannel_id>/', SubChannelView.as_view(), name='subchannel-detail'),
    path('groups/', GroupView.as_view(), name='group-list'),
    path('groups/<int:group_id>/', GroupView.as_view(), name='group-detail'),
    path('channels/create/', ChannelView.as_view(), name='create-channel'),
]
