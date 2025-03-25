from rest_framework import serializers
import ast

from user.serializers import UserSerializer
from .models import MFA, Channel, ChannelMembers, ChannelModeration, Group, InviteLink, MessageCCFromChannel, Permission, PermissionAssignment, SecurityAction, SubChannel, SubChannelGroupMembers, SubChannelMembers

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'owner', 'name', 'description', 'logo']


class ChannelSerializer2(serializers.ModelSerializer):
    blocked_members = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = '__all__'

    def get_blocked_members(self, obj):
        blocked_members = obj.channel_member.filter(status=5)  # Assuming status=5 means 'Blocked'
        return UserSerializer([member.user for member in blocked_members], many=True).data
    

class ChannelMembersSerializer1(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = ['id', 'owner', 'name', 'description', 'logo', 'members']

    def get_members(self, obj):
        members = ChannelMembers.objects.filter(channel=obj, status__in=[1, 2, 3, 4, 9, 10])
        return UserSerializer([member.user for member in members], many=True).data
    
    
class SubChannelMembersSerializer1(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = SubChannel
        fields = ['id', 'name', 'description', 'logo', 'members']

    def get_members(self, obj):
        members = SubChannelMembers.objects.filter(sub_channel=obj, status__in=[1, 2, 3, 4, 9, 10])
        return UserSerializer([member.user for member in members], many=True).data
    
    
    
class GroupMembersSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'logo', 'members']

    def get_members(self, obj):
        members = SubChannelGroupMembers.objects.filter(group=obj, status__in=[1, 2, 3, 4, 9, 10])
        return UserSerializer([member.user for member in members], many=True).data

    
class ChannelOwnerSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = ['id', 'owner', 'name', 'description', 'logo']

    def get_owner(self, obj):
        return UserSerializer(obj.owner, many=False).data

class SubChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubChannel
        fields = ['channel', 'name', 'description']

class SubGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
    permission_type = serializers.CharField(source='get_permission_type_display')

    class Meta:
        model = Permission
        fields = '__all__'


class ChannelMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelMembers
        fields = ['user', 'status', 'type']

class PermissionAssignmentSerializer(serializers.ModelSerializer):
    permission = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)
    members = serializers.SerializerMethodField()

    class Meta:
        model = PermissionAssignment
        fields = ['id', 'permission', 'permission_type', 'target_id', 'target_type', 'all_members', 'members']

    def get_members(self, obj):
        # Initialize an empty list for filtered members
        filtered_members = []

        # Handle members based on the target_type
        if obj.target_type == 'community' and obj.target_id and obj.permission_type:
            # Fetch channel members related to the community
            channel_members = ChannelMembers.objects.filter(channel__id=obj.target_id)

        elif obj.target_type == 'sub-community' and obj.target_id and obj.permission_type:
            # Fetch channel members related to the sub-community
            channel_members = SubChannelMembers.objects.filter(sub_channel__id=obj.target_id)

        elif obj.target_type == 'group' and obj.target_id and obj.permission_type:
            # Fetch channel members related to the group
            channel_members = SubChannelGroupMembers.objects.filter(group__id=obj.target_id)

        else:
            return []  # If no valid target_type, return an empty list

        # Filter the members based on permission type
        for channel_member in channel_members:
            # Ensure the member's type is a list and has the required permission
            print("hhhhhhhhhhhhhhhhh", channel_member.type)
            if isinstance(channel_member.type, str):
                channel_member.type = ast.literal_eval(channel_member.type)
            if isinstance(channel_member.type, list) and channel_member.type:
                print("hhhhhhhhhhhhhhhhh 1", channel_member)
                print("hhhhhhhhhhhhhhhhh 1 check", obj.permission_type)
                if obj.permission_type in channel_member.type:
                    print("hhhhhhhhhhhhhhhhh 2", channel_member)
                    filtered_members.append(channel_member)

        # Serialize and return the filtered members
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", filtered_members)
        return ChannelMemberSerializer(filtered_members, many=True).data



class CommunitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Channel
        fields = '__all__'



class ChannelJoinSerializer(serializers.Serializer):
    class Meta:
        model = Channel
        fields = '__all__'


class SubChannelJoinSerializer(serializers.Serializer):
    class Meta:
        model = SubChannel
        fields = '__all__'


class GroupJoinSerializer(serializers.Serializer):
    class Meta:
        model = Group
        fields = '__all__'

class ChannelMembersSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = ChannelMembers
        fields = ["channel", "user", "type", "status", "permissions"]

    def get_permissions(self, obj):
        assigned_P = PermissionAssignment.objects.filter(permission_type=obj.type)
        return PermissionAssignmentSerializer(assigned_P, many=True).data
    

class InviteLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteLink
        fields = ['invite_link']



class InviteLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteLink
        fields = ['token', 'created_at', 'updated_at']
        



class MFADataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MFA
        fields = ['code']        
        
        
class SecurityActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityAction
        fields = ['user', 'channel', 'pause_invites', 'pause_dms', 'pause_duration', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
        
        
class MessageCCFromChannelSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    parent_message = serializers.PrimaryKeyRelatedField(queryset=MessageCCFromChannel.objects.all(), required=False, allow_null=True)

    class Meta:
        model = MessageCCFromChannel
        fields = ['id', 'subject', 'message', 'channel', 'user', 'created_at', 'parent_message', 'replies']

    def get_replies(self, obj):
        # If this message is a reply (has a parent_message), don't return any replies
        if obj.parent_message:
            return None  # Or return [] if you'd prefer an empty array
        # Otherwise, return all replies for this message
        return MessageCCFromChannelSerializer(obj.replies.all(), many=True).data
    
    
    
class ChannelModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelModeration
        fields = ['message_request', 'direct_message', 'mute_channel']
        
        
     