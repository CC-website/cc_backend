# urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ChannelCRUDView, ChannelView, GetBanedMembers, PerformActionOnMembers, PermissionAssignmentAPIView, PermissionAssignmentListView, PermissionRemovalAPIView, SubChannelView, GroupView,
    PermissionTypeViewSet, ChannelViewSet
)

# Router for default viewsets
router = DefaultRouter()
# router.register(r'channels', ChannelViewSet, basename='channel')

urlpatterns = [
    # Permission types endpoint
    path('permissions/types/', PermissionTypeViewSet.as_view({'get': 'list'}), name='permission-types'),
    path('permissions/list/', PermissionAssignmentListView.as_view(), name='permissions-list'), 

    # Permission assignment endpoint
    path('permissions/assign/', PermissionAssignmentAPIView.as_view(), name='permission-assignments'),
    path('permissions/assign/<int:pk>/', PermissionAssignmentAPIView.as_view(), name='permission-assignment-detail'),
    path('permissions/assign/<int:target_id>/<target_type>', PermissionAssignmentAPIView.as_view(), name='permission-assignment-detail-v2'),
    
    
    path('permissions/remove-user-role/', PermissionRemovalAPIView.as_view(), name='remove-user-role'),

    path('permissions/perform-action-on-members/', PerformActionOnMembers.as_view(), name='perform-action-on-members'),
    path('channels/owner/<int:channel_id>', PerformActionOnMembers.as_view(), name='channel-owner'),
    path('channels/baned-members/<int:channel_id>', GetBanedMembers.as_view(), name='baned-members/'),
    
    
    # Channels endpoints
    path('channels/', ChannelView.as_view(), name='channel-list'),
    path('channels/<int:channel_id>/', ChannelView.as_view(), name='channel-detail'),
    path('channels/delete/<int:channel_id>/', ChannelView.as_view(), name='channel-delete'),
    path('channels/create/', ChannelView.as_view(), name='create-channel'),
    path('channels/add_members/', ChannelCRUDView.as_view(), name='channel-add-members'),
    path('channels/<int:pk>/', ChannelCRUDView.as_view(), name='channel-detail-crud'),
    path('channels/<int:pk>/members/', ChannelViewSet.as_view({'get': 'get_members'}), name='channel-members'),
    path('channels/<int:pk>/admins/', ChannelViewSet.as_view({'get': 'get_admins'}), name='admins'),
    path('channels/<int:pk>/blocked-members/', ChannelViewSet.as_view({'get': 'get_blocked_members'}), name='blocked-members'),
    path('channels/<int:pk>/move-to-admins/', ChannelViewSet.as_view({'post': 'move_to_admins'}), name='move-to-admins'),
    path('channels/<int:pk>/move-to-blocked-members/', ChannelViewSet.as_view({'post': 'move_to_blocked_members'}), name='move-to-blocked-members'),
    path('channels/<int:pk>/delete-member/', ChannelViewSet.as_view({'post': 'delete_member'}), name='delete-member'),
    path('channels/<int:pk>/move-from-blocked-members/', ChannelViewSet.as_view({'post': 'move_from_blocked_members'}), name='move-from-blocked-members'),
    path('channels/<int:pk>/move-from-admins/', ChannelViewSet.as_view({'post': 'move_from_admins'}), name='move-from-admins'),

    # Subchannels endpoints
    path('subchannels/', SubChannelView.as_view(), name='subchannel-list'),
    path('subchannels/<int:subchannel_id>/', SubChannelView.as_view(), name='subchannel-detail'),
    path('subchannels/delete/<int:subchannel_id>/', SubChannelView.as_view(), name='subchannel-detail'),

    # Groups endpoints
    path('groups/', GroupView.as_view(), name='group-list'),
    path('groups/<int:group_id>/', GroupView.as_view(), name='group-detail'),
]
