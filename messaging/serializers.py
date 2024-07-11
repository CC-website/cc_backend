from rest_framework import serializers
from .models import Message, GroupChat

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [ 'user', 'content', 'timestamp']

class GroupChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupChat
        fields = ['id', 'name', 'members']
