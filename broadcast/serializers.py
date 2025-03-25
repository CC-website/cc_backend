from datetime import timedelta
from rest_framework import serializers
from .models import Broadcast
from django.utils import timezone

class BroadcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broadcast
        fields = ['id', 'content_type', 'content_id', 'created_at', 'closed_at', 'is_active']
        read_only_fields = ['created_at', 'closed_at', 'is_active']  # Make these fields read-only

    def create(self, validated_data):
        # Set the user to the logged-in user
        validated_data['user'] = self.context['request'].user
        
        # Automatically set closed_at based on created_at
        validated_data['closed_at'] = timezone.now() + timedelta(days=3)

        return super().create(validated_data)

    def validate(self, attrs):
        # Optionally add any additional validation logic here
        return attrs