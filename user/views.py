import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from .models import User

from .serializers import UserRegistrationSerializer, UserSerializer  # Make sure to import your serializer

from django.contrib.auth.forms import AuthenticationForm
from rest_framework.authtoken.models import Token

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import authentication_classes, permission_classes

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import jwt
import time
import json

from django.core.validators import validate_email
from django.core.exceptions import ValidationError



class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = UserRegistrationSerializer(data=request.data)

            # Check if email is sent in the request data
            email = request.data.get('email', '')
            if email:
                try:
                    # Validate the email format
                    validate_email(email)
                except ValidationError:
                    return Response({'message': 'Invalid email format.'}, status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                email = serializer.validated_data.get('email')
                phone_number = serializer.validated_data.get('phone_number')
                print(email)
                if email and User.objects.filter(email=email).exists():
                    return Response({'message': 'Email address already exists. Please use a different email.'}, status=status.HTTP_400_BAD_REQUEST)

                if phone_number and User.objects.filter(phone_number=phone_number).exists():
                    return Response({'message': 'Phone number already exists. Please use a different phone number.'}, status=status.HTTP_400_BAD_REQUEST)
                print("Nigel", email)
                user = serializer.save()

                authenticated_user = authenticate(request, username=user.username, password=serializer.validated_data['password'])
                
                if authenticated_user is not None:
                    login(request, authenticated_user)
                else:
                    return Response({'message': 'Failed to log in user after registration.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                refresh = RefreshToken.for_user(authenticated_user)
                token = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }

                user_data = {
                    'username': authenticated_user.username,
                    'email': authenticated_user.email,
                } if authenticated_user.email else {
                    'username': authenticated_user.username,
                    'phone_number': authenticated_user.phone_number,
                }

                return Response({'message': 'User registered and logged in successfully', 'user': user_data, 'token': token}, status=status.HTTP_201_CREATED)

            return Response({'message': 'Error creating user. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle other exceptions or log the error
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        print(request.data.get('username'))
        form = AuthenticationForm(request, data=request.data)
        # print(form)
        if form.is_valid():
            print("the name of the people")
            # Check if the login data contains a phone number or an email
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print('Nigel', username)
            user = None
            if '@' in username:
                user = User.objects.filter(email=username).first()
            else:
                user = User.objects.filter(phone_number=username).first()
            
            if user:
                authenticated_user = authenticate(request, username=user.username, password=password)
            else:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if authenticated_user:
                login(request, authenticated_user)
                
                refresh = RefreshToken.for_user(authenticated_user)
                token = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                
                # Include additional user information in the response
                user_data = {
                    'username': authenticated_user.username,
                }
                if authenticated_user.email:
                    user_data['email'] = authenticated_user.email
                if authenticated_user.phone_number:
                    user_data['phone_number'] = authenticated_user.phone_number

                return Response({'token': token, 'user': user_data}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # Form validation failed, return an error response with details
            error_message = "Invalid credentials"
            if form.errors:
                error_message = form.errors.as_json()
            return Response({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)



class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            logout(request)
            return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Error logging out: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    




class UserInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)




class CheckLogin(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            print("Checking login status...")

            # Get the user from the request object
            user = request.user

            # Prepare user data based on whether email or phone number is available
            user_data = {
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number
            }

            print("User is authenticated.")
            return Response({'message': 'User is logged in', 'user': user_data}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f'Error checking login status: {str(e)}')
            return Response({'message': f'Error checking login status: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)