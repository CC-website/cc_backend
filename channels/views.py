from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.forms.models import model_to_dict
from django.views import View
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Channel, SubChannel, Group


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
    def get(self, request, channel_id=None):
        if channel_id:
            channel = get_object_or_404(Channel, pk=channel_id)
            data = model_to_dict(channel)
        else:
            channels = Channel.objects.all()
            data = serializers.serialize('json', channels)
        return JsonResponse(data, safe=False)

    def post(self, request):
        data = request.POST.dict()
        channel = Channel.objects.create(**data)
        return JsonResponse(model_to_dict(channel), status=201)

    def put(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        data = dict(request.PUT.items())
        for key, value in data.items():
            setattr(channel, key, value)
        channel.save()
        return JsonResponse(model_to_dict(channel))

    def delete(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        channel.delete()
        return JsonResponse({'message': 'Channel deleted successfully'}, status=204)


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
        data = request.POST.dict()
        subchannel = SubChannel.objects.create(**data)
        return JsonResponse(model_to_dict(subchannel), status=201)

    def put(self, request, subchannel_id):
        subchannel = get_object_or_404(SubChannel, pk=subchannel_id)
        data = dict(request.PUT.items())
        for key, value in data.items():
            setattr(subchannel, key, value)
        subchannel.save()
        return JsonResponse(model_to_dict(subchannel))

    def delete(self, request, subchannel_id):
        subchannel = get_object_or_404(SubChannel, pk=subchannel_id)
        subchannel.delete()
        return JsonResponse({'message': 'Subchannel deleted successfully'}, status=204)


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
        data = request.POST.dict()
        group = Group.objects.create(**data)
        return JsonResponse(model_to_dict(group), status=201)

    def put(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        data = dict(request.PUT.items())
        for key, value in data.items():
            setattr(group, key, value)
        group.save()
        return JsonResponse(model_to_dict(group))

    def delete(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        group.delete()
        return JsonResponse({'message': 'Group deleted successfully'}, status=204)
