# urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    ChannelCRUDView, ChannelModerationView, ChannelView, GetAllChannelMembers, GetAllGroupMembers, GetAllSubChannelMembers, GetBanedMembers, GetChannelOwner, InviteLinkView, JoinView, MFAViewSet, MessageCCFromChannelCreateView, PerformActionOnMembers, PermissionAssignmentAPIView, PermissionAssignmentListView, PermissionRemovalAPIView, SecurityActionView, SubChannelPermissionCheckerView, SubChannelView, GroupView,
    PermissionTypeViewSet, ChannelViewSet, UserMessageCCFromChannelView
)

# Router for default viewsets
router = DefaultRouter()
# router.register(r'get_channels', ChannelViewSet, basename='channel')
# router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'mfa/(?P<channel_id>\d+)', MFAViewSet, basename='mfa')

urlpatterns = [
    path('', include(router.urls)),
    path('get_channels/', ChannelViewSet.as_view({'get': 'list'}), name='channel-list'),
    path('get_channels/<int:pk>/', ChannelViewSet.as_view({'get': 'retrieve'}), name='channel-detail'),

    # Permission types endpoint
    path('permissions/types/', PermissionTypeViewSet.as_view({'get': 'list'}), name='permission-types'),
    path('permissions/list/', PermissionAssignmentListView.as_view(), name='permissions-list'),

    # Permission assignment endpoints
    path('permissions/assign/', PermissionAssignmentAPIView.as_view(), name='permission-assignments'),
    path('permissions/assign/<int:pk>/', PermissionAssignmentAPIView.as_view(), name='permission-assignment-detail'),
    path('permissions/assign/<int:target_id>/<target_type>/', PermissionAssignmentAPIView.as_view(), name='permission-assignment-detail-v2'),
    path('permissions/remove-user-role/', PermissionRemovalAPIView.as_view(), name='remove-user-role'),

    # Action on members
    path('permissions/perform-action-on-members/', PerformActionOnMembers.as_view(), name='perform-action-on-members'),

    # Channels endpoints
    path('channels/', ChannelView.as_view(), name='channel-list'),
    path('channels/<int:channel_id>/', ChannelView.as_view(), name='channel-detail'),
    path('channels/owner/<int:channel_id>/', GetChannelOwner.as_view(), name='channel-owner'),
    path('channels/delete/<int:channel_id>/', ChannelView.as_view(), name='channel-delete'),
    path('channels/create/', ChannelView.as_view(), name='create-channel'),
    path('channels/add-members/', ChannelCRUDView.as_view(), name='channel-add-members'),
    path('channels/<int:channel_id>/members/', GetAllChannelMembers.as_view(), name='channel-members'),
    path('channels/<int:pk>/admins/', ChannelViewSet.as_view({'get': 'get_admins'}), name='channel-admins'),
    path('channels/<int:pk>/blocked-members/', ChannelViewSet.as_view({'get': 'get_blocked_members'}), name='blocked-members'),
    path('channels/<int:pk>/move-to-admins/', ChannelViewSet.as_view({'post': 'move_to_admins'}), name='move-to-admins'),
    path('channels/<int:pk>/move-to-blocked-members/', ChannelViewSet.as_view({'post': 'move_to_blocked_members'}), name='move-to-blocked-members'),
    path('channels/<int:pk>/delete-member/', ChannelViewSet.as_view({'post': 'delete_member'}), name='delete-member'),
    path('channels/<int:pk>/move-from-blocked-members/', ChannelViewSet.as_view({'post': 'move_from_blocked_members'}), name='move-from-blocked-members'),
    path('channels/<int:pk>/move-from-admins/', ChannelViewSet.as_view({'post': 'move_from_admins'}), name='move-from-admins'),

    # Subchannels endpoints
    path('subchannels/', SubChannelView.as_view(), name='subchannel-list'),
    path('subchannels/<int:subchannel_id>/', SubChannelView.as_view(), name='subchannel-detail'),
    path('subchannels/delete/<int:subchannel_id>/', SubChannelView.as_view(), name='subchannel-delete'),
    path('subchannels/<int:sub_channel_id>/members/', GetAllSubChannelMembers.as_view(), name='subchannel-members'),
    path('subchannels/members/', GetAllSubChannelMembers.as_view(), name='add_subchannel_members'),
    
    # Groups endpoints
    path('groups/', GroupView.as_view(), name='group-list'),
    path('groups/<int:group_id>/', GroupView.as_view(), name='group-detail'),
    path('groups/<int:group_id>/members/', GetAllGroupMembers.as_view(), name='group-members'),
    path('groups/members/', GetAllGroupMembers.as_view(), name='add_group_members'),
    
    # Banned members endpoint
    path('channels/banned-members/<int:channel_id>/', GetBanedMembers.as_view(), name='banned-members'),
    path('channels/<int:channel_id>/invite-link/', InviteLinkView.as_view(), name='invite-link'),
    path('community_action/', JoinView.as_view(), name='follow-community'),
    
    # security actions endpoint
    path('security-actions/<int:channel_id>/', SecurityActionView.as_view(), name='security-actions'),
    path('CCmessages-from-channel/', UserMessageCCFromChannelView.as_view(), name='message-create'),
    path('CCmessages-from-channel/user/', UserMessageCCFromChannelView.as_view(), name='user-messages'),
    path('moderation-actions/<int:channel_id>/', ChannelModerationView.as_view(), name='channel-moderation-actions'),
]