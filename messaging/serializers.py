from rest_framework import serializers

from user.models import Message
from .models import  GroupChat

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [ 'user', 'content', 'timestamp']

class GroupChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupChat
        fields = ['id', 'name', 'members']
