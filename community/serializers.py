from rest_framework import serializers

from user.serializers import UserSerializer
from .models import Channel, Group, Permission, PermissionAssignment, SubChannel

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['owner', 'name', 'description', 'logo']

class ChannelSerializer2(serializers.ModelSerializer):
    blocked_members = UserSerializer(many=True)

    class Meta:
        model = Channel
        fields = '__all__'

        

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
        fields = ['id', 'permission_type', 'exception_users']


class PermissionAssignmentSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True)  # Use UserSerializer for members field

    class Meta:
        model = PermissionAssignment
        fields = '__all__'
