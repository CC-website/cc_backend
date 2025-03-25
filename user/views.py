import time
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from .models import ChatSettings, User

from .serializers import ChatSettingsSerializer, UserRegistrationSerializer, UserSerializer  # Make sure to import your serializer

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
import base64
from django.core.files.base import ContentFile
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from rest_framework import viewsets
from rest_framework.response import Response
from .models import PrivacySettings, PrivacyExceptions
from .serializers import PrivacySettingsSerializer, PrivacyExceptionsSerializer
from rest_framework.decorators import action



class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = UserRegistrationSerializer(data=request.data)

            # Check if email is sent in the request data
            print("nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn: ", request)
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
                    'id': user.id,
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
    
    def put(self, request, *args, **kwargs):
        user = request.user
        username = request.data.get("username", None)
        about = request.data.get("about", None)
        phone_number = request.data.get("phone_number", None)
        email = request.data.get("email", None)
        image_base64 = request.data.get("profile_picture", None)

        image_data = None
        if image_base64 and ';base64,' in image_base64:
            _, imgstr = image_base64.split(';base64,')
            ext = 'png'
            image_data = ContentFile(base64.b64decode(imgstr), name=f"{username}_{user.id}_profile.{ext}")

        user_data = User.objects.filter(id=user.id).first()
        if username is not None:
            user_data.username = username
        if about is not None:
            user_data.about = about
        if phone_number is not None:
            user_data.phone_number = phone_number
        if email is not None:
            user_data.email = email
        if image_data is not None:
            user_data.profile_picture = image_data
        
        user_data.save()

        serializer = UserSerializer(user_data)
        response = serializer.data
        print(response)
        return Response(response, status=200)




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
        


class GetUsers(APIView):

    @staticmethod
    def process_phone_number(phone_number):
        # Remove any non-digit characters from the phone number
        cleaned_number = ''.join(filter(str.isdigit, phone_number))

        # If the number starts with a country code, remove it
        if cleaned_number.startswith('237') and len(cleaned_number) > 9:
            cleaned_number = cleaned_number[3:]

        # If the number starts with a '+' sign, remove it
        if cleaned_number.startswith('+'):
            cleaned_number = cleaned_number[1:]

        # If the number starts with '1' (for US country code), remove it
        if cleaned_number.startswith('1') and len(cleaned_number) == 11:
            cleaned_number = cleaned_number[1:]

        return cleaned_number
    

    def post(self, request, *args, **kwargs):
        try:
            contacts = request.data.get('contacts', [])
            processed_contacts = []
            processed_identifiers = set()  # Set to store processed phone numbers or emails
            count = 0

            for contact in contacts:
                if contact.get("phoneNumbers"):
                    number = contact.get("phoneNumbers")[0]['number']
                    search_item = self.process_phone_number(number)
                    if search_item not in processed_identifiers:
                        user = User.objects.filter(phone_number=search_item).first()
                        if user:
                            processed_contact = {
                                'id': count,
                                'user_id': user.pk,
                                'name': user.username,
                                'phone_number': user.phone_number,
                                'profile_picture': user.profile_picture.url,
                                'about': user.about
                            }
                        else:
                            processed_contact = {
                                'id': count,
                                'name': contact.get("name", ""),
                                'phone_number': contact.get("phoneNumbers")[0]['number'],
                                'about': 'Sorry I am not on CC.'
                            }
                        processed_contacts.append(processed_contact)
                        processed_identifiers.add(search_item)
                        count += 1  # Increment count
                elif contact.get("emails", ""):
                    search_item = contact.get("emails")[0]['email']
                    if search_item not in processed_identifiers:
                        user = User.objects.filter(email=search_item).first()
                        if user:
                            
                            processed_contact = {
                                'id': count,
                                'user_id': user.pk,
                                'name': user.username,
                                'email': user.email,
                                'profile_picture': user.profile_picture.url,
                                'about': user.about
                            }
                        else:
                            processed_contact = {
                                'id': count,
                                'name': contact.get("name", ""),
                                'email': contact.get("emails")[0]['email'],
                                'about': 'Sorry I am not on CC.'
                            }
                        processed_contacts.append(processed_contact)
                        processed_identifiers.add(search_item)
                        count += 1  # Increment count

            return Response({'data': processed_contacts}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Error processing contacts: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PrivacySettingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the privacy settings for the authenticated user
        user = request.user
        privacy_settings = get_object_or_404(PrivacySettings, user=user)

        serializer = PrivacySettingsSerializer(privacy_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        # Get the authenticated user
        user = request.user

        # Extract type and option from request data
        type = request.data.get('type')
        option = request.data.get('option')
        callOption = request.data.get('callOption', None)
        messageValue = request.data.get('messageValue', None)
        if callOption is not None:
            option = bool(callOption)
        elif messageValue is not None:
            print('Nigel', messageValue)
            option = messageValue
        else:
            option = int(option)


        # Check if both type and option are provided
        if type is None or option is None:
            return Response({'error': 'Both "type" and "option" must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the provided type is a valid field in PrivacySettings
        valid_fields = [field.name for field in PrivacySettings._meta.get_fields()]
        if type not in valid_fields:
            return Response({'error': f'Invalid privacy setting type: {type}'}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create privacy settings for the authenticated user
        privacy_settings, _ = PrivacySettings.objects.get_or_create(user=user)

        # Update the privacy settings
        setattr(privacy_settings, type, option)
        privacy_settings.save()

        # Serialize and return the updated privacy settings
        serializer = PrivacySettingsSerializer(privacy_settings)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    

class PrivacyExceptionsViewSet(viewsets.ModelViewSet):
    queryset = PrivacyExceptions.objects.all()
    serializer_class = PrivacyExceptionsSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    



class ChatSettingsDetail(APIView):
    def get_object(self):
        user = self.request.user
        try:
            return ChatSettings.objects.get(user=user)
        except ChatSettings.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        chat_settings = self.get_object()
        serializer = ChatSettingsSerializer(chat_settings)
        return Response(serializer.data)

    def patch(self, request, format=None):
        chat_settings = self.get_object()
        serializer = ChatSettingsSerializer(chat_settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

def messaging(request):
    return render(request, 'user/index.html')





class CheckContacts(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logged_in_user = request.user  # Get logged-in user
            current_user = User.objects.get(pk=logged_in_user.id)

            print(f"Logged-in user phone: {current_user.phone_number}")

            # Extract the contacts from request data
            request_contacts = request.data

            # Ensure that request_contacts is a list
            if not isinstance(request_contacts, list):
                print("request data", request.data)

                user_contact = None
                user = None

                if isinstance(request.data, str):
                    if "@" in request.data and "." in request.data:  # Basic email validation
                        user_contact = request.data
                        user = User.objects.get(email=user_contact)
                    elif request.data.isdigit():  # Check if it's a number
                        user_contact = request.data
                        user = User.objects.get(phone_number=user_contact)

                print("Email:", user)
                name = f'{user.first_name} {user.last_name}'.strip() or user.username
                image = user.profile_picture.url if user.profile_picture else None

                # Default type is 'single'
                contact_type = 'single'

                # If the matched contact is the logged-in user, change type to 'self'
                if user.id == current_user.id:
                    contact_type = 'self'
            
                contact_list = {
                        "id": user.id,
                        "contact": user_contact,
                        "name": name,
                        "lastMessage": user.about,
                        "image": image,
                        "lastMessageTime": "",
                        "about": user.about,
                        "unreadCount": 0,
                        "type": contact_type,
                        "favorite": False,
                    }

                # Return the response as JSON
                return Response(contact_list, status=status.HTTP_200_OK)
                

            contact_list = []
            users = User.objects.all()
            
            print(request.data)

            for user in users:
                calling_code = user.code.get('callingCode', '') if isinstance(user.code, dict) else ''
                contact = f"{calling_code}{user.phone_number}"

                # Check if the user's contact matches any contact in request data
                if contact in request_contacts or user.phone_number in request_contacts:
                    name = f'{user.first_name} {user.last_name}'.strip() or user.username
                    image = user.profile_picture.url if user.profile_picture else None

                    # Default type is 'single'
                    contact_type = 'single'

                    # If the matched contact is the logged-in user, change type to 'self'
                    if user.id == current_user.id:
                        contact_type = 'self'

                    contact_list.append({
                        "id": user.id,
                        "contact": contact,
                        "name": name,
                        "lastMessage": user.about,
                        "image": image,
                        "lastMessageTime": "",
                        "about": user.about,
                        "unreadCount": 0,
                        "type": contact_type,
                        "favorite": False,
                    })

            # Return the response as JSON
            return Response(contact_list, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
    
    