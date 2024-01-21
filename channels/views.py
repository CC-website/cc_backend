from django.shortcuts import get_object_or_404
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.forms.models import model_to_dict
from django.views import View
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Channel, SubChannel, Group

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Channel
from .serializers import ChannelSerializer, SubChannelSerializer, SubGroupSerializer
from rest_framework.parsers import MultiPartParser, FormParser
import json
from django.views.decorators.http import require_POST
import base64
from django.core.files.base import ContentFile


@method_decorator(csrf_exempt, name='dispatch')
@swagger_auto_schema(
    operation_description="CRUD for channels",
    operation_id="channels",
    tags=["Channels"],
    responses={
        200: openapi.Response("Successful operation", [
            {
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'image_url': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True),
            }
        ]),
        404: openapi.Response("Not Found"),
        401: openapi.Response("Unauthorized"),
    }
)
class ChannelView(View):
    
    parser_classes = (MultiPartParser, FormParser,)

    def get(self, request: HttpRequest):
        channels = Channel.objects.all()
        data = []

        for channel in channels:
            channel_data = model_to_dict(channel, fields=['id', 'name', 'description'])
            
            # Construct the complete image URL using the request object
            channel_data['image_url'] = request.build_absolute_uri(channel.logo.url) if channel.logo else None
            
            channel_data['subchannels'] = []

            subchannels = SubChannel.objects.filter(channel=channel)
            for subchannel in subchannels:
                subchannel_data = model_to_dict(subchannel, fields=['id', 'name', 'description'])
                
                # Construct the complete image URL for subchannels
                subchannel_data['image_url'] = request.build_absolute_uri(subchannel.logo.url) if subchannel.logo else None
                
                subchannel_data['groups'] = []

                groups = Group.objects.filter(subchannel=subchannel)
                for group in groups:
                    group_data = model_to_dict(group, fields=['id', 'name', 'description'])
                    
                    # Construct the complete image URL for groups
                    group_data['image_url'] = request.build_absolute_uri(group.logo.url) if group.logo else None
                    
                    subchannel_data['groups'].append(group_data)

                channel_data['subchannels'].append(subchannel_data)

            data.append(channel_data)

        return JsonResponse(data, safe=False)
    

    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data.get('name', '')
            description = data.get('description', '')
            image_base64 = data.get('image', '')
            print(name)

            # Initialize image_data with None
            image_data = None

            # Decode base64 image data
            if image_base64 and ';base64,' in image_base64:
                format, imgstr = image_base64.split(';base64,')  # Extract the format and base64 part
                ext = format.split('/')[-1]  # Extract the image extension
                image_data = ContentFile(base64.b64decode(imgstr), name=f"{name}_logo.{ext}")

            # Now, you can process the data and save it to the database using a serializer
            serializer = ChannelSerializer(data={'name': name, 'description': description, 'logo': image_data})
            
            if serializer.is_valid():
                serializer.save()
                print(serializer.data)
                return JsonResponse(serializer.data, status=201)
            print('Nigel')
            return JsonResponse(serializer.errors, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    def put(self, request, channel_id):
        try:
            # Fetch the existing channel
            channel = Channel.objects.get(pk=channel_id)

            data = json.loads(request.body)
            name = data.get('name', None)
            description = data.get('description', None)
            image_base64 = data.get('image', None)

            # Check if a new image is provided
            if image_base64 and ';base64,' in image_base64:
                format, imgstr = image_base64.split(';base64,')  # Extract the format and base64 part
                ext = format.split('/')[-1]  # Extract the image extension
                image_data = ContentFile(base64.b64decode(imgstr), name=f"{name}_logo.{ext}")
                channel.logo = image_data

            # Update channel data if non-empty and non-null
            if name is not None:
                channel.name = name
            if description is not None:
                channel.description = description

            channel.save()

            # Return updated channel data
            serializer = ChannelSerializer(channel)
            return JsonResponse(serializer.data, status=200)

        except Channel.DoesNotExist:
            return JsonResponse({'error': 'Channel not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    def delete(self, request, channel_id):
        try:
            # Fetch the existing channel
            channel = Channel.objects.filter(id=channel_id).first()
            print(channel.name)
            channel.delete()
            return JsonResponse({'message': 'Channel deleted successfully'}, status=200)
        except Channel.DoesNotExist:
            return JsonResponse({'error': 'Channel not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@swagger_auto_schema(
    operation_description="CRUD for subchannels",
    operation_id="subchannels",
    tags=["Subchannels"],
    responses={
        200: openapi.Response("Successful operation", [
            {
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'image_url': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True),
            }
        ]),
        404: openapi.Response("Not Found"),
        401: openapi.Response("Unauthorized"),
    }
)
class SubChannelView(View):

    def get(self, request, subchannel_id=None):
        if subchannel_id:
            subchannel = get_object_or_404(SubChannel, pk=subchannel_id)
            data = model_to_dict(subchannel)
        else:
            subchannels = SubChannel.objects.all()
            data = serializers.serialize('json', subchannels)
        return JsonResponse(data, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
            channel_id = data.get('channel_id', '')
            name = data.get('name', '')
            description = data.get('description', '')
            print(name)
            print(description)
            print(channel_id)
            
            # Now, you can process the data and save it to the database using a serializer
            serializer = SubChannelSerializer(data={'channel':channel_id, 'name': name, 'description': description})
            
            if serializer.is_valid():
                serializer.save()
                print(serializer.data)
                return JsonResponse(serializer.data, status=201)
            print('Nigel')
            return JsonResponse(serializer.errors, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    def put(self, request, subchannel_id):
        try:
            # Fetch the existing channel
            channel = SubChannel.objects.get(pk=subchannel_id)

            data = json.loads(request.body)
            name = data.get('name', None)
            description = data.get('description', None)

            # Update channel data if non-empty and non-null
            if name is not None:
                channel.name = name
            if description is not None:
                channel.description = description

            channel.save()

            # Return updated channel data
            serializer = SubChannelSerializer(channel)
            return JsonResponse(serializer.data, status=200)

        except SubChannel.DoesNotExist:
            return JsonResponse({'error': 'Channel not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    def delete(self, request, subchannel_id):
        try:
            # Fetch the existing channel
            channel = SubChannel.objects.filter(id=subchannel_id).first()
            print(channel.name)
            channel.delete()
            return JsonResponse({'message': 'Channel deleted successfully'}, status=200)
        except SubChannel.DoesNotExist:
            return JsonResponse({'error': 'Channel not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@swagger_auto_schema(
    operation_description="CRUD for groups",
    operation_id="groups",
    tags=["Groups"],
    responses={
        200: openapi.Response("Successful operation", [
            {
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'image_url': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True),
            }
        ]),
        404: openapi.Response("Not Found"),
        401: openapi.Response("Unauthorized"),
    }
)
class GroupView(View):
    def get(self, request, group_id=None):
        if group_id:
            group = get_object_or_404(Group, pk=group_id)
            data = model_to_dict(group)
        else:
            groups = Group.objects.all()
            data = serializers.serialize('json', groups)
        return JsonResponse(data, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
            subchannel_id = data.get('subchannel', '')
            name = data.get('name', '')
            description = data.get('description', '')
            image_base64 = data.get('image', '')

            # Initialize image_data with None
            image_data = None

            # Decode base64 image data
            if image_base64 and ';base64,' in image_base64:
                format, imgstr = image_base64.split(';base64,')  # Extract the format and base64 part
                ext = format.split('/')[-1]  # Extract the image extension
                image_data = ContentFile(base64.b64decode(imgstr), name=f"{name}_logo.{ext}")

            # Now, you can process the data and save it to the database using a serializer
            serializer = SubGroupSerializer(data={'subchannel':subchannel_id, 'name': name, 'description': description, 'logo': image_data})
            
            if serializer.is_valid():
                serializer.save()
                print(serializer.data)
                return JsonResponse(serializer.data, status=201)
            print('Nigel')
            return JsonResponse(serializer.errors, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)


    def put(self, request, group_id):
        try:
            # Fetch the existing channel
            channel = Group.objects.get(pk=group_id)

            data = json.loads(request.body)
            name = data.get('name', None)
            description = data.get('description', None)

            # Update channel data if non-empty and non-null
            if name is not None:
                channel.name = name
            if description is not None:
                channel.description = description

            channel.save()

            # Return updated channel data
            serializer = SubGroupSerializer(channel)
            return JsonResponse(serializer.data, status=200)

        except Group.DoesNotExist:
            return JsonResponse({'error': 'Channel not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    def delete(self, request, group_id):
        try:
            # Fetch the existing channel
            channel = Group.objects.filter(id=group_id).first()
            print(channel.name)
            channel.delete()
            return JsonResponse({'message': 'Channel deleted successfully'}, status=200)
        except Group.DoesNotExist:
            return JsonResponse({'error': 'Channel not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
