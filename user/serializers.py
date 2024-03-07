from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    code = serializers.DictField(write_only=True, required=False, allow_null=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'phone_number', 'code']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        # Ensure that either email or phone_number is provided
        if not (data.get('email') or data.get('phone_number')):
            raise serializers.ValidationError("Either email or phone_number must be provided.")
        
        return data

    def create(self, validated_data):
        # Create a new user with hashed password
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email'),
            phone_number=validated_data.get('phone_number'),
            password=make_password(validated_data['password']),
            code=validated_data['code'],
        )
        return user

    def to_representation(self, instance):
        # Generate JWT token and include it in the response
        refresh = RefreshToken.for_user(instance)
        token_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return {
            'username': instance.username,
            'email': instance.email,
            'phone_number': instance.phone_number,
            'token': token_data,
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email', 'phone_number', 'code']