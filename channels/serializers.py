from rest_framework import serializers
from .models import Channel, Group, SubChannel

class ChannelSerializer(serializers.ModelSerializer):
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