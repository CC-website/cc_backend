import uuid
from django.shortcuts import get_object_or_404
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.forms.models import model_to_dict
from django.views import View
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics
from rest_framework.decorators import action
import ast

from user.models import User
from user.serializers import UserSerializer
from .models import MFA, Channel, ChannelMembers, InviteLink, Permission, PermissionAssignment, SubChannel, Group, SubChannelGroupMembers, SubChannelMembers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Channel
from .serializers import ChannelJoinSerializer, ChannelMembersSerializer, ChannelMembersSerializer1, ChannelOwnerSerializer, ChannelSerializer, ChannelSerializer2, CommunitySerializer, GroupJoinSerializer, GroupMembersSerializer, InviteLinkSerializer, MFADataSerializer, PermissionAssignmentSerializer, PermissionSerializer, SubChannelJoinSerializer, SubChannelMembersSerializer1, SubChannelSerializer, SubGroupSerializer
from rest_framework.parsers import MultiPartParser, FormParser
import json
from django.views.decorators.http import require_POST
import base64
from django.core.files.base import ContentFile

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from rest_framework import viewsets, mixins




class ChannelPermissionCheckerView(View):
    def get_user_permissions(self, user):
        # Correct field name for the relationship
        channels = Channel.objects.filter(
            Q(owner=user) | Q(channel_member__user=user, channel_member__status__in=[1, 2, 3, 4, 9, 10])
        )
        user_permissions_dict = {}

        for channel in channels:
            permission_assignments = PermissionAssignment.objects.filter(
                target_id=channel.id,
                target_type='community'  # Match target type to the appropriate value
            )

            user_channel_permissions = []
            if channel.owner == user:
                user_channel_permissions.append('owner')

            for assignment in permission_assignments:
                # Check permissions only if the user is not in the exception list
                for permission in assignment.permission.all():
                    if assignment.all_members or user not in permission.exception_users.all():
                        user_channel_permissions.append(permission.get_permission_type_display())

            user_permissions_dict[channel.id] = {'user_permissions': user_channel_permissions}

        return user_permissions_dict if user_permissions_dict else None

    def get(self, request):
        user = request.user
        user_permissions = self.get_user_permissions(user)

        if user_permissions:
            return JsonResponse(user_permissions)
        else:
            return JsonResponse({'message': 'User does not have permissions for any channel.'}, status=404)



class SubChannelPermissionCheckerView(View):
    def get_user_permissions(self, user):
        # Correct field name for the relationship
        subchannels = SubChannel.objects.filter(
            Q(channel__owner=user) | Q(sub_channel_member__user=user)
        ).distinct()

        user_permissions_dict = {}

        for subchannel in subchannels:
            user_subchannel_permissions = []

            if subchannel.channel.owner == user:
                user_subchannel_permissions.append('admin')

            member_permissions = SubChannelMembers.objects.filter(sub_channel=subchannel, user=user).first()
            if member_permissions:
                user_subchannel_permissions.append('member')

                permission_assignments = PermissionAssignment.objects.filter(
                    target_id=subchannel.id,
                    target_type='sub-community'  # Match target type to the appropriate value
                )

                for assignment in permission_assignments:
                    # Check permissions only if the user is not in the exception list
                    for permission in assignment.permission.all():
                        if user not in permission.exception_users.all():
                            user_subchannel_permissions.append(permission.get_permission_type_display())

            user_permissions_dict[subchannel.id] = {'user_permissions': user_subchannel_permissions}

        return user_permissions_dict if user_permissions_dict else None

    def get(self, request):
        user = request.user
        user_permissions = self.get_user_permissions(user)

        if user_permissions:
            return JsonResponse(user_permissions)
        else:
            return JsonResponse({'message': 'User does not have permissions for any subchannel.'}, status=404)



class GroupPermissionCheckerView(View):
    def get_user_permissions(self, user):
        # Correct field name for the relationship
        groups = Group.objects.filter(
            Q(subchannel__channel__owner=user) | Q(sub_channel_group_member__user=user)
        ).distinct()

        user_permissions_dict = {}

        for group in groups:
            user_group_permissions = []

            if group.subchannel.channel.owner == user:
                user_group_permissions.append('admin')

            member_permissions = SubChannelGroupMembers.objects.filter(group=group, user=user).first()
            if member_permissions:
                user_group_permissions.append('member')

                permission_assignments = PermissionAssignment.objects.filter(
                    target_id=group.id,
                    target_type='group'  # Match target type to the appropriate value
                )

                for assignment in permission_assignments:
                    # Check permissions only if the user is not in the exception list
                    for permission in assignment.permission.all():
                        if user not in permission.exception_users.all():
                            user_group_permissions.append(permission.get_permission_type_display())

            user_permissions_dict[group.id] = {'user_permissions': user_group_permissions}

        return user_permissions_dict if user_permissions_dict else None

    def get(self, request):
        user = request.user
        user_permissions = self.get_user_permissions(user)

        if user_permissions:
            return JsonResponse(user_permissions)
        else:
            return JsonResponse({'message': 'User does not have permissions for any group.'}, status=404)



class ChannelView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser,)

    def post(self, request):
        try:
            data = request.data
            name = data.get('name', '')
            description = data.get('description', '')
            image_base64 = data.get('image', '')
            image_data = None

            if image_base64 and ';base64,' in image_base64:
                format, imgstr = image_base64.split(';base64,')
                ext = format.split('/')[-1]
                image_data = ContentFile(base64.b64decode(imgstr), name=f"{name}_logo.{ext}")
            
            user = User.objects.filter(id=request.user.id).first()
            channel_data = {'owner': user.id, 'name': name, 'description': description, 'logo': image_data}
            
            serializer = ChannelSerializer(data=channel_data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def get(self, request, *args, **kwargs):
        try:
            # Retrieve permissions for channels, subchannels, and groups
            channel_permissions = ChannelPermissionCheckerView().get_user_permissions(request.user)
            subchannel_permissions = SubChannelPermissionCheckerView().get_user_permissions(request.user)
            group_permissions = GroupPermissionCheckerView().get_user_permissions(request.user)
            
            # Initialize data list to hold serialized data
            data = []
            
            if channel_permissions:
                channels = Channel.objects.filter(id__in=channel_permissions.keys())

                for channel in channels:
                    channel_data = model_to_dict(channel, fields=['id', 'name', 'description'])
                    channel_data['image_url'] = request.build_absolute_uri(channel.logo.url) if channel.logo else None
                    channel_data['subchannels'] = []

                    if subchannel_permissions:
                        subchannels = SubChannel.objects.filter(channel=channel, id__in=subchannel_permissions.keys())
                        
                        for subchannel in subchannels:
                            subchannel_data = model_to_dict(subchannel, fields=['id', 'name', 'description'])
                            subchannel_data['image_url'] = request.build_absolute_uri(subchannel.logo.url) if subchannel.logo else None
                            subchannel_data['groups'] = []

                            if group_permissions:
                                groups = Group.objects.filter(subchannel=subchannel, id__in=group_permissions.keys())

                                for group in groups:
                                    group_data = model_to_dict(group, fields=['id', 'name', 'description'])
                                    group_data['image_url'] = request.build_absolute_uri(group.logo.url) if group.logo else None
                                    subchannel_data['groups'].append(group_data)

                            channel_data['subchannels'].append(subchannel_data)

                    data.append(channel_data)

                return Response(data, status=200)
            return Response({'error': 'Channel not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def put(self, request, channel_id):
        try:
            channel = Channel.objects.get(pk=channel_id)
            data = request.data
            name = data.get('name', '')
            description = data.get('description', '')
            image_base64 = data.get('image', '')
            image_data = None

            if image_base64 and ';base64,' in image_base64:
                format, imgstr = image_base64.split(';base64,')
                ext = format.split('/')[-1]
                image_data = ContentFile(base64.b64decode(imgstr), name=f"{name}_logo.{ext}")
            
            if name:
                channel.name = name
            if description:
                channel.description = description
            if image_data:
                channel.logo = image_data

            channel.save()
            serializer = ChannelSerializer(channel)
            return Response(serializer.data, status=200)

        except Channel.DoesNotExist:
            return Response({'error': 'Channel not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def delete(self, request, channel_id):
        try:
            channel = Channel.objects.get(id=channel_id)
            channel.delete()
            return Response({'message': 'Channel deleted successfully'}, status=200)
        except Channel.DoesNotExist:
            return Response({'error': 'Channel not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)




class SubChannelView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser,)

    def post(self, request):
        try:
            data = request.data
            channel_id = data.get('channel_id')
            name = data.get('name', '')
            description = data.get('description', '')
            image_base64 = data.get('image', '')
            image_data = None

            if image_base64 and ';base64,' in image_base64:
                format, imgstr = image_base64.split(';base64,')
                ext = format.split('/')[-1]
                image_data = ContentFile(base64.b64decode(imgstr), name=f"{name}_logo.{ext}")

            channel = Channel.objects.filter(id=channel_id).first()
            if not channel:
                return Response({'error': 'Channel not found'}, status=404)

            subchannel = SubChannel.objects.create(
                channel=channel,
                name=name,
                description=description,
                logo=image_data
            )

            serializer = SubChannelSerializer(subchannel)
            return Response(serializer.data, status=201)
        
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def put(self, request, subchannel_id):
        try:
            print("Nigel")
            subchannel = SubChannel.objects.get(pk=subchannel_id)
            data = request.data
            name = data.get('name', '')
            description = data.get('description', '')
            image_base64 = data.get('image', '')
            image_data = None

            if image_base64 and ';base64,' in image_base64:
                format, imgstr = image_base64.split(';base64,')
                ext = format.split('/')[-1]
                image_data = ContentFile(base64.b64decode(imgstr), name=f"{name}_logo.{ext}")

            if name:
                subchannel.name = name
            if description:
                subchannel.description = description
            if image_data:
                subchannel.logo = image_data

            subchannel.save()
            serializer = SubChannelSerializer(subchannel)
            return Response(serializer.data, status=200)

        except SubChannel.DoesNotExist:
            return Response({'error': 'Subchannel not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def delete(self, request, subchannel_id):
        try:
            subchannel = SubChannel.objects.get(id=subchannel_id)
            subchannel.delete()
            return Response({'message': 'Subchannel deleted successfully'}, status=200)
        except SubChannel.DoesNotExist:
            return Response({'error': 'Subchannel not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class GroupView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser,)

    def post(self, request):
        try:
            data = request.data
            subchannel_id = data.get('subchannel')
            name = data.get('name', '')
            description = data.get('description', '')
            image_base64 = data.get('image', '')
            image_data = None

            if image_base64 and ';base64,' in image_base64:
                format, imgstr = image_base64.split(';base64,')
                ext = format.split('/')[-1]
                image_data = ContentFile(base64.b64decode(imgstr), name=f"{name}_logo.{ext}")

            subchannel = SubChannel.objects.filter(id=subchannel_id).first()
            if not subchannel:
                return Response({'error': 'Subchannel not found'}, status=404)

            group = Group.objects.create(
                subchannel=subchannel,
                name=name,
                description=description,
                logo=image_data
            )

            serializer = SubGroupSerializer(group)
            return Response(serializer.data, status=201)
        
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def put(self, request, group_id):
        try:
            group = Group.objects.get(pk=group_id)
            data = request.data
            name = data.get('name', '')
            description = data.get('description', '')
            image_base64 = data.get('image', '')
            image_data = None

            if image_base64 and ';base64,' in image_base64:
                format, imgstr = image_base64.split(';base64,')
                ext = format.split('/')[-1]
                image_data = ContentFile(base64.b64decode(imgstr), name=f"{name}_logo.{ext}")

            if name:
                group.name = name
            if description:
                group.description = description
            if image_data:
                group.logo = image_data

            group.save()
            serializer = SubGroupSerializer(group)
            return Response(serializer.data, status=200)

        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def delete(self, request, group_id):
        try:
            group = Group.objects.get(id=group_id)
            group.delete()
            return Response({'message': 'Group deleted successfully'}, status=200)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)



class ChannelCRUDView(APIView):
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            channel = self.get_channel(pk)
            if not channel:
                return Response({'error': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.serializer_class(channel)
            return Response(serializer.data)
        else:
            channels = Channel.objects.all()
            serializer = self.serializer_class(channels, many=True)
            return Response(serializer.data)

    def post(self, request):
        name = request.data.getlist('name')[0]  # Get the list and then the first element
        channel_id = request.data.getlist('channel_id')[0]  # Get the list and then the first element
        selected_contact_ids = request.data.getlist('selectedContactIds')  # Get the list directly

        channel_permissions = ChannelPermissionCheckerView().get_user_permissions(request.user)

        if channel_permissions and int(channel_id) in list(channel_permissions.keys()):
            # Retrieve permissions for the specific channel ID
            user_permissions = channel_permissions.get(int(channel_id), {}).get('user_permissions', [])

            # Assuming 'owner' permission is always present
            owner_permissions = [perm['permissions'] for perm in user_permissions if 'owner' in perm.values()]
            if owner_permissions:
                # User is an owner, proceed with the action
                print("User is an owner.")

                # Convert selected_contact_ids to a list of integers
                selected_user_ids = [int(user_id) for user_id in selected_contact_ids]

                # Retrieve the Channel instance using the provided channel_id
                try:
                    channel = Channel.objects.get(id=channel_id)
                except Channel.DoesNotExist:
                    print("Channel does not exist.")
                    return Response({"message": "Channel does not exist."}, status=status.HTTP_404_NOT_FOUND)

                # Add selected users to the members field of the Channel instance
                try:
                    # Get User instances for the selected user IDs
                    selected_users = User.objects.filter(id__in=selected_user_ids)
                    # Filter out selected users that are already members of the channel
                    selected_users = selected_users.exclude(id__in=channel.members.all())
                    # Add selected users to the members field
                    channel.members.add(*selected_users)
                    # Save the changes
                    channel.save()

                    # Retrieve and return all members in the channel
                    members = channel.members.all()
                    member_ids = [member.id for member in members]
                    print('Nigel Nigel', member_ids)
                    print("Selected users added to the channel successfully.")
                    return Response({"message": "Selected users added to the channel successfully.", "members": member_ids})
                except Exception as e:
                    print("Error:", e)
                    return Response({"message": "Error adding selected users to the channel."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                # User is not an owner
                print("User is not an owner.")
                return Response({"message": "User is not an owner."}, status=status.HTTP_403_FORBIDDEN)

        else:
            # User does not have permissions for the specified channel
            print("User does not have permissions for the specified channel.")
            return Response({"message": "User does not have permissions for the specified channel."}, status=status.HTTP_403_FORBIDDEN)

    
    
    
    def put(self, request, pk):
        channel = self.get_channel(pk)
        if not channel:
            return Response({'error': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(channel, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        channel = self.get_channel(pk)
        if not channel:
            return Response({'error': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)
        channel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_channel(self, pk):
        try:
            return Channel.objects.get(pk=pk)
        except Channel.DoesNotExist:
            return None
        


class PermissionAssignmentAPIView(APIView):
    def get(self, request, target_id, target_type):
        try:
            roles = PermissionAssignment.objects.filter(target_type=target_type, target_id=target_id)
            data = []

            if roles.exists():
                for role in roles:
                    serializer = PermissionAssignmentSerializer(role)
                    # Retrieve and format permissions
                    permission_ids = serializer.data.get('permission', [])
                    permission_array = [
                        perm.get_permission_type_display()
                        for perm in Permission.objects.filter(id__in=permission_ids)
                    ]
                    
                    # Create a copy of the serialized data and update the permissions
                    updated_data = serializer.data.copy()
                    updated_data['permission'] = permission_array
                    data.append(updated_data)
                
                return Response(data, status=status.HTTP_200_OK)
            
            return Response({'message': 'No roles available'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        permissions_ids = request.data.get('permission', [])
        all_members = request.data.get('all_members', False)
        permission_type = request.data.get('permission_type')
        target_id = request.data.get('target_id')
        target_type = request.data.get('target_type')

        # Validate target_type against defined choices
        if target_type not in ['community', 'sub-community', 'group']:
            return Response(
                {'error': 'Invalid target type.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the serializer instance with incoming data
        serializer = PermissionAssignmentSerializer(data={
            'permission': permissions_ids,
            'permission_type': permission_type,
            'target_id': target_id,
            'target_type': target_type,
            'all_members': all_members
        })

        # Handle member-specific logic
        if 'members' in request.data:
            members = request.data.get('members', [])

            # Filter ChannelMembers by target_id for the relevant target_type
            if target_type == 'community':
                channel_members = ChannelMembers.objects.filter(channel__id=target_id)
            elif target_type == 'sub-community':
                channel_members = SubChannelMembers.objects.filter(sub_channel__id=target_id)
            elif target_type == 'group':
                channel_members = SubChannelGroupMembers.objects.filter(group__id=target_id)

            for member in channel_members:
                if member.type is None:
                    member.type = []

                # Ensure member.type is a list
                if not isinstance(member.type, list):
                    if isinstance(member.type, str):
                        member.type = ast.literal_eval(member.type)
                    else:
                        continue

                # Add or remove the permission type based on members
                if member.user.id not in members:
                    if permission_type in member.type:
                        member.type.remove(permission_type)
                elif member.user.id in members:
                    if permission_type and permission_type not in member.type:
                        member.type.append(permission_type)

                # Save only if changes were made
                member.save()

        if serializer.is_valid():
            # Check if the permission assignment already exists for the specific target
            existing_assignment = PermissionAssignment.objects.filter(
                permission__in=permissions_ids,
                permission_type=permission_type,
                target_id=target_id,
                target_type=target_type
            ).exists()

            if existing_assignment:
                return Response(
                    {'error': f"{permission_type} already exists for this {target_type}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save the new permission assignment
            permission_assignment = serializer.save()
            permission_assignment.permission.set(permissions_ids)
            permission_assignment.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Return serializer errors if validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    
    def put(self, request):
        permission_assignment_id = request.data.get('permission_assignment_id')

        if not permission_assignment_id:
            return Response({"error": "Permission assignment ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            permission_assignment = PermissionAssignment.objects.get(pk=permission_assignment_id)
        except PermissionAssignment.DoesNotExist:
            return Response({"error": "Permission assignment not found."}, status=status.HTTP_404_NOT_FOUND)

        # Handle permission updates
        if 'permissions_updates' in request.data:
            permission_data = request.data.get('permissions_updates')
            new_permission_ids = [data['id'] for data in permission_data]

            # Clear existing permissions and add new ones
            permission_assignment.permission.clear()
            permission_assignment.permission.add(*new_permission_ids)
            return Response({"message": "Update successful"}, status=status.HTTP_200_OK)

        permission_type = request.data.get('permission_type')
        old_permission_type = request.data.get('old_permission_type', None)
        all_users = request.data.get('all_members')
        target_id = request.data.get('target_id')
        target_type = request.data.get('target_type')

        if 'old_permission_type' in request.data and permission_type is not None:
            # Choose the appropriate model based on target_type
            if target_type == 'community':
                channel_members = ChannelMembers.objects.filter(channel__id=target_id)
            elif target_type == 'sub-community':
                channel_members = SubChannelMembers.objects.filter(sub_channel__id=target_id)
            elif target_type == 'group':
                channel_members = SubChannelGroupMembers.objects.filter(group__id=target_id)
            else:
                return Response({"error": "Invalid target type."}, status=status.HTTP_400_BAD_REQUEST)

            # Process members' permission types
            for member in channel_members:
                member.type = self.parse_member_type(member.type)
                if old_permission_type in member.type:
                    member.type = [permission_type if t == old_permission_type else t for t in member.type]
                member.save()

        permission_assignment.permission_type = permission_type
        if all_users is not None:
            permission_assignment.all_members = all_users

        # Handle members permission assignment if provided
        if 'members' in request.data:
            members = request.data.get('members', [])

            # Retrieve members based on the target type
            if permission_assignment.target_type == 'community':
                channel_members = ChannelMembers.objects.filter(channel__id=permission_assignment.target_id)
            elif permission_assignment.target_type == 'sub-community':
                channel_members = SubChannelMembers.objects.filter(sub_channel__id=permission_assignment.target_id)
            elif permission_assignment.target_type == 'group':
                channel_members = SubChannelGroupMembers.objects.filter(group__id=permission_assignment.target_id)
            else:
                return Response({"error": "Invalid target type."}, status=status.HTTP_400_BAD_REQUEST)

            # Update members' permissions
            for member in channel_members:
                member.type = self.parse_member_type(member.type)  # Ensure member.type is a list
                if member.user.id not in members:
                    if permission_type in member.type:
                        member.type.remove(permission_type)
                else:
                    if permission_type not in member.type:
                        member.type.append(permission_type)
                member.save()

            return Response({"message": "Update successful"}, status=status.HTTP_200_OK)

        permission_assignment.save()
        serializer = PermissionAssignmentSerializer(permission_assignment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def parse_member_type(self, member_type):
        """Helper method to parse the member type field safely."""
        if isinstance(member_type, str):
            try:
                return eval(member_type) if member_type else []
            except Exception as e:
                print(f"Error parsing member type: {e}")
                return []
        return member_type if isinstance(member_type, list) else []



    def delete(self, request):
        permission_assignment_id = request.data.get('permission_assignment_id')
        
        try:
            permission_assignment = PermissionAssignment.objects.get(pk=permission_assignment_id)
            permission_type = permission_assignment.permission_type
            target_id = permission_assignment.target_id
            target_type = permission_assignment.target_type

            # Remove the permission from all members based on the target type
            if target_type == 'community':
                channel_members = ChannelMembers.objects.filter(channel__id=target_id)
            elif target_type == 'sub-community':
                channel_members = SubChannelMembers.objects.filter(sub_channel__id=target_id)
            elif target_type == 'group':
                channel_members = SubChannelGroupMembers.objects.filter(group__id=target_id)
            else:
                return Response({"error": "Invalid target type."}, status=status.HTTP_400_BAD_REQUEST)

            # Iterate through members and remove the permission type from their list
            for member in channel_members:
                member.type = self.parse_member_type(member.type)  # Ensure member.type is a list
                if permission_type in member.type:
                    member.type.remove(permission_type)
                member.save()

            # Now delete the PermissionAssignment
            permission_assignment.delete()
            return Response({'message': 'PermissionAssignment deleted successfully, and permissions removed from members'}, status=status.HTTP_204_NO_CONTENT)
        
        except PermissionAssignment.DoesNotExist:
            return Response({"error": "PermissionAssignment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class PermissionTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        target_type = self.request.query_params.get('target_type')
        print("000000000000000000000000000000000000000000000:",target_type)
        if target_type:
            queryset = queryset.filter(target_type=target_type)
        return queryset



class PermissionAssignmentListView(generics.ListAPIView):
    serializer_class = ChannelMembersSerializer

    def get_queryset(self):
        target_id = self.request.query_params.get('target_id')
        return ChannelMembers.objects.filter(channel__id=target_id, status__in=[1, 2, 3, 4, 9, 10])
    
class PermissionRemovalAPIView(APIView):
    
    def put(self, request):
        for role in request.data.get('permissions_to_remove'):
            permission = PermissionAssignment.objects.get(pk=role)
            permission.members.remove(request.data.get('user_id'))
        return Response({'Message': "user successfully removed"}, status=status.HTTP_200_OK)
    


class PerformActionOnMembers(APIView):

    def get(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        user = get_object_or_404(User, pk=channel.owner.id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        action = request.data.get('action')
        channel_id = request.data.get('channel_id')
        user_id = request.data.get('user_id')

        # Fetch the channel
        channel = get_object_or_404(Channel, pk=channel_id)

        # Check if user_id is a list when it shouldn't be
        if isinstance(user_id, list) and action != 'restore':
            return Response({'error': 'User ID should not be a list for this action.'}, status=status.HTTP_400_BAD_REQUEST)
        elif not isinstance(user_id, list) and action == 'restore':
            return Response({'error': 'User ID should be a list for the restore action.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the target user
            user = get_object_or_404(User, pk=user_id) if not isinstance(user_id, list) else None
            member = get_object_or_404(ChannelMembers, channel=channel, user=user) if user else None
        except TypeError:
            return Response({'error': 'Invalid user ID format. Expected a number.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the requesting user is the channel owner
        is_owner = channel.owner == request.user

        # Initialize permissions array to store permissions for the member
        permissions_array = set()

        # Get assigned permissions based on member's type, only if not the owner
        if not is_owner and member:
            assigned_permissions = PermissionAssignment.objects.filter(permission_type__in=member.type)
            for ap in assigned_permissions:
                for p in ap.permission.all():
                    permissions_array.add(p.permission_type)  # Using a set to keep permissions unique

        # Perform actions based on the specified action
        if action == 'band':
            # Owner can perform any action without permission check
            if is_owner or 3 in permissions_array:
                member.status = 5  # Blocked
                member.save()
                return Response({'message': 'User has been banned'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Sorry, you do not have permission to ban members.'}, status=status.HTTP_403_FORBIDDEN)

        elif action == 'kick':
            # Owner can perform any action without permission check
            if is_owner or 4 in permissions_array:
                member.status = 6  # Removed
                member.save()
                return Response({'message': 'User has been removed from the channel'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Sorry, you do not have permission to remove members.'}, status=status.HTTP_403_FORBIDDEN)

        elif action == 'transfer':
            # Owner can perform any action without permission check
            if is_owner or 0 in permissions_array:
                channel.Original_owner = channel.owner
                channel.owner = user
                channel.save()
                member.user = channel.owner
                member.type = [1]  # Assuming '1' represents some specific role type
                member.save()
                return Response({'message': 'Ownership has been transferred'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Sorry, you do not have permission to transfer ownership.'}, status=status.HTTP_403_FORBIDDEN)

        elif action == 'restore':
            # Handle restoring multiple users, owner can perform any action without permission check
            if is_owner or 5 in permissions_array:  # Assuming '5' is permission for restoring
                if isinstance(user_id, list):
                    restored_users = []
                    for data in user_id:
                        user = get_object_or_404(User, pk=data)
                        member = get_object_or_404(ChannelMembers, channel=channel, user=user)
                        if member.status == 5:  # Only restore if the user was blocked
                            member.status = 1  # Active
                            member.save()
                            restored_users.append(user.id)
                    return Response({'message': f'Restored users: {restored_users}'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid data format for user IDs'}, status=status.HTTP_400_BAD_REQUEST)

        # If the action does not match any known action
        return Response({'error': 'Invalid action specified'}, status=status.HTTP_400_BAD_REQUEST)
    


class MFAViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin):
    serializer_class = MFADataSerializer
    
    
    @action(detail=False, methods=['GET'], url_path='')
    def get(self, request, *args, **kwargs):
        channel_id = self.kwargs.get('channel_id')
        try:
            return  Response(MFADataSerializer(MFA.objects.get(channel_id=channel_id)).data,  status=status.HTTP_200_OK)
        except MFA.DoesNotExist:
            return Response({'error': 'MFA not found for this channel'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['POST'], url_path='create')
    def create_MFA(self, request, *args, **kwargs):
        channel_id = self.kwargs.get('channel_id')
        try:
            Channel.objects.get(id=channel_id)
            mfa, created = MFA.objects.get_or_create(channel_id=channel_id)
            mfa.generate_code()
            mfa.save()
            serializer = self.get_serializer(mfa)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Channel.DoesNotExist:
            return Response({'error': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['POST'], url_path='regenerate')
    def regenerate_code(self, request, *args, **kwargs):
        channel_id = self.kwargs.get('channel_id')
        if not channel_id:
            return Response({'error': 'Channel ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            mfa = MFA.objects.get(channel_id=channel_id)
            mfa.generate_code()
            mfa.save()
            serializer = self.get_serializer(mfa)
            return Response({'code': mfa.code}, status=status.HTTP_200_OK)
        except MFA.DoesNotExist:
            return Response({'error': 'MFA code not found for this channel'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['POST'], url_path='verify')
    def verify_code(self, request, *args, **kwargs):
        channel_id = self.kwargs.get('channel_id')
        code = request.data.get('code')
        
        if not channel_id or not code:
            return Response({'error': 'Channel ID and code are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            mfa = MFA.objects.get(channel_id=channel_id)
            if mfa.code == code:
                return Response({'success': True}, status=status.HTTP_200_OK)
            else:
                return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
        except MFA.DoesNotExist:
            return Response({'error': 'MFA code not found for this channel'}, status=status.HTTP_404_NOT_FOUND)
        
        
    @action(detail=False, methods=['DELETE'], url_path='disable')
    def disable_MFA(self, request, *args, **kwargs):
        channel_id = self.kwargs.get('channel_id')
        
        if not channel_id:
            return Response({'error': 'Channel ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Check if the channel exists
            Channel.objects.get(id=channel_id)
            
            # Retrieve and delete the MFA record
            mfa = MFA.objects.get(channel_id=channel_id)
            mfa.delete()
            
            return Response({'success': 'MFA disabled successfully'}, status=status.HTTP_204_NO_CONTENT)
        
        except Channel.DoesNotExist:
            return Response({'error': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except MFA.DoesNotExist:
            return Response({'error': 'MFA record not found for this channel'}, status=status.HTTP_404_NOT_FOUND)


class GetBanedMembers(APIView):

    def get(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        serializer = ChannelSerializer2(channel)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetAllChannelMembers(APIView):

    def get(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        serializer = ChannelMembersSerializer1(channel)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetAllSubChannelMembers(APIView):

    def get(self, request, sub_channel_id):
        subchannel = get_object_or_404(SubChannel, id=sub_channel_id)
        serializer = SubChannelMembersSerializer1(subchannel)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Access JSON data directly from request.data
        sub_channel_id = request.data.get('sub_channel_id')
        members_list = request.data.get('members', [])  # Default to empty list if no members are provided

        # Ensure members_list is a list
        if not isinstance(members_list, list):
            return Response({'detail': 'Invalid members data format'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the SubChannel instance
        subchannel = get_object_or_404(SubChannel, id=sub_channel_id)
        
        is_owner = request.user == subchannel.channel.owner

        # Initialize permissions array to store permissions for the member
        permissions_array = set()
        
        member_type = []
        channel = Channel.objects.filter(id=subchannel.channel.id).first()
        
        # Check the member type in the channel
        channel_member = ChannelMembers.objects.filter(channel=channel, user=request.user).first()
        if channel_member:
            member_type.append(channel_member.type)

        # Check the member type in the subchannel
        subchannel_member = SubChannelMembers.objects.filter(sub_channel=subchannel, user=request.user).first()
        if subchannel_member:
            member_type.append(subchannel_member.type)

        # Check assigned permissions based on the user's role, if not the owner
        if not is_owner:
            if channel_member:
                assigned_permissions = PermissionAssignment.objects.filter(
                    permission_type__in=channel_member.type, 
                    target_id=subchannel.id, 
                    target_type='sub-community'
                )
                for ap in assigned_permissions:
                    for p in ap.permission.all():
                        permissions_array.add(p.permission_type)

            # If the user does not have permission to add/remove members, return a 403 Forbidden
            if 1 not in permissions_array and 4 not in permissions_array:  # 1 = 'Add Members', 4 = 'Remove Members'
                return Response({'detail': 'You do not have permission to manage members in this subchannel.'}, status=status.HTTP_403_FORBIDDEN)

        # Get the current members of the subchannel
        current_members = SubChannelMembers.objects.filter(sub_channel=subchannel).order_by('id')

        # Extract current member user IDs while maintaining order
        current_member_ids = list(current_members.values_list('user_id', flat=True))

        # Ensure incoming members list is a list of IDs in order
        incoming_member_ids = list(map(int, members_list))

        print("Members to be added or reordered:", incoming_member_ids)
        print("Current members:", current_member_ids)

        # First, check if the incoming list is exactly the same as the current (in terms of order)
        if incoming_member_ids == current_member_ids:
            return Response({'detail': 'No changes needed, members are already up to date'}, status=status.HTTP_200_OK)

        # Determine members to add and remove (ignoring order for now)
        current_member_set = set(current_member_ids)
        incoming_member_set = set(incoming_member_ids)

        members_to_add = incoming_member_set - current_member_set  # Members in incoming but not in current
        members_to_remove = current_member_set - incoming_member_set  # Members in current but not in incoming

        # Handle adding new members
        for member_id in members_to_add:
            user = get_object_or_404(User, id=member_id)
            SubChannelMembers.objects.create(sub_channel=subchannel, user=user, status=4)

        # Handle removing members no longer part of the subchannel
        SubChannelMembers.objects.filter(sub_channel=subchannel, user_id__in=members_to_remove).delete()

        # Handle reordering (if members to remove/add were empty, this will adjust the order)
        if members_to_add or members_to_remove:
            # Only reorder if changes were made to members
            remaining_members = [m for m in incoming_member_ids if m not in members_to_remove]
            for idx, member_id in enumerate(remaining_members):
                member = SubChannelMembers.objects.filter(sub_channel=subchannel, user_id=member_id).first()
                if member:
                    member.status = 4  # Update status if necessary or some other reordering logic
                    member.save()
        else:
            # Reordering logic without changing members
            for idx, member_id in enumerate(incoming_member_ids):
                member = SubChannelMembers.objects.filter(sub_channel=subchannel, user_id=member_id).first()
                if member:
                    member.status = 4  # You can use this to represent the order if needed
                    member.save()

        return Response({'detail': 'Subchannel members updated and reordered successfully'}, status=status.HTTP_200_OK)



class GetAllGroupMembers(APIView):

    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        serializer = GroupMembersSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Access JSON data directly from request.data
        group_id = request.data.get('group_id')
        members_list = request.data.get('members', [])  # Default to empty list if no members are provided
        # Ensure members_list is a list
        if not isinstance(members_list, list):
            return Response({'detail': 'Invalid members data format'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the Group instance
        group = get_object_or_404(Group, id=group_id)
        
        is_owner = request.user == group.subchannel.channel.owner

        # Initialize permissions array to store permissions for the member
        permissions_array = set()
        
        member_type = []
        channel = Channel.objects.filter(id=group.subchannel.channel.id).first()
        
        # Check the member type in the channel
        channel_member = ChannelMembers.objects.filter(channel=channel, user=request.user).first()
        if channel_member:
            member_type.append(channel_member.type)

        # Check the member type in the group
        group_member = SubChannelGroupMembers.objects.filter(group=group, user=request.user).first()
        if group_member:
            member_type.append(group_member.type)

        # Check assigned permissions based on the user's role, if not the owner
        if not is_owner:
            if channel_member:
                assigned_permissions = PermissionAssignment.objects.filter(
                    permission_type__in=channel_member.type, 
                    target_id=group.id, 
                    target_type='group'
                )
                for ap in assigned_permissions:
                    for p in ap.permission.all():
                        permissions_array.add(p.permission_type)

            # If the user does not have permission to add/remove members, return a 403 Forbidden
            if 1 not in permissions_array and 4 not in permissions_array:  # 1 = 'Add Members', 4 = 'Remove Members'
                return Response({'detail': 'You do not have permission to manage members in this group.'}, status=status.HTTP_403_FORBIDDEN)

        # Get the current members of the group
        current_members = SubChannelGroupMembers.objects.filter(group=group).order_by('id')

        # Extract current member user IDs while maintaining order
        current_member_ids = list(current_members.values_list('user_id', flat=True))

        # Ensure incoming members list is a list of IDs in order
        incoming_member_ids = list(map(int, members_list))

        print("Members to be added or reordered:", incoming_member_ids)
        print("Current members:", current_member_ids)

        # First, check if the incoming list is exactly the same as the current (in terms of order)
        if incoming_member_ids == current_member_ids:
            return Response({'detail': 'No changes needed, members are already up to date'}, status=status.HTTP_200_OK)

        # Determine members to add and remove (ignoring order for now)
        current_member_set = set(current_member_ids)
        incoming_member_set = set(incoming_member_ids)

        members_to_add = incoming_member_set - current_member_set  # Members in incoming but not in current
        members_to_remove = current_member_set - incoming_member_set  # Members in current but not in incoming

        # Handle adding new members
        for member_id in members_to_add:
            user = get_object_or_404(User, id=member_id)
            SubChannelGroupMembers.objects.create(group=group, user=user, status=4)

        # Handle removing members no longer part of the group
        SubChannelGroupMembers.objects.filter(group=group, user_id__in=members_to_remove).delete()

        # Handle reordering (if members to remove/add were empty, this will adjust the order)
        if members_to_add or members_to_remove:
            # Only reorder if changes were made to members
            remaining_members = [m for m in incoming_member_ids if m not in members_to_remove]
            for idx, member_id in enumerate(remaining_members):
                member = SubChannelGroupMembers.objects.filter(group=group, user_id=member_id).first()
                if member:
                    member.status = 4  # Update status if necessary or some other reordering logic
                    member.save()
        else:
            # Reordering logic without changing members
            for idx, member_id in enumerate(incoming_member_ids):
                member = SubChannelGroupMembers.objects.filter(group=group, user_id=member_id).first()
                if member:
                    member.status = 4  # You can use this to represent the order if needed
                    member.save()

        return Response({'detail': 'Group members updated and reordered successfully'}, status=status.HTTP_200_OK)


  

class GetAllgroupeMembers(APIView):

    def get(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        serializer = ChannelMembersSerializer1(channel)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetChannelOwner(APIView):

    def get(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        serializer = ChannelOwnerSerializer(channel)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ChannelViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    


@method_decorator(csrf_exempt, name='dispatch')
class JoinView(APIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self, target_type):
        """Dynamically return the appropriate serializer based on target_type."""
        if target_type == 'channel':
            return ChannelJoinSerializer
        elif target_type == 'subchannel':
            return SubChannelJoinSerializer
        elif target_type == 'group':
            return GroupJoinSerializer
        return None

    def post(self, request, *args, **kwargs):
        data = request.data
        target_type = data.get('target_type')
        target_id = data.get('target_id')
        target_action = data.get('target_action')
        user = request.user
        membership_data = []

        if not target_type or not target_id or not target_action:
            return Response({'error': 'target_type, target_id, and target_action are required'}, status=status.HTTP_400_BAD_REQUEST)

        serializer_class = self.get_serializer_class(target_type)
        if serializer_class is None:
            return Response({'error': 'Invalid target type'}, status=status.HTTP_400_BAD_REQUEST)

        target = get_object_or_404(serializer_class.Meta.model, id=target_id)

        if target_type == 'channel':
            status_value = 1 if target.open else 0  # 1 for Active, 0 for Requested
            channel_member, created = ChannelMembers.objects.get_or_create(channel=target, user=user)
            if target_action == 'following':
                channel_member.status = 8 if channel_member.status == 7 else 7
            elif target_action == 'connecting':
                channel_member.status = 11 if channel_member.status == 10 else (0 if target.open else 10)
            channel_member.save()
            user_channel_membership = ChannelMembers.objects.filter(user=user)
            for member in user_channel_membership:
                membership_data.append({
                    'id': member.id,
                    'status': member.get_status_display(),
                    'target': {
                        'id': target_id,
                        'name': target.name,
                    }
                })
            message = 'Joined channel successfully' if target.open else 'Channel join request sent'
        
        elif target_type == 'subchannel':
            status_value = 1 if target.open else 0  # 1 for Active, 0 for Requested
            subchannel_member, created = SubChannelMembers.objects.get_or_create(sub_channel=target, user=user)
            if target_action == 'following':
                subchannel_member.status = 8 if subchannel_member.status == 7 else 7
            elif target_action == 'connecting':
                subchannel_member.status = 11 if subchannel_member.status == 10 else (10 if not target.open else subchannel_member.status)
            subchannel_member.save()
            user_channel_membership = ChannelMembers.objects.filter( user=user)
            for member in user_channel_membership:
                membership_data.append({
                    'id': member.id,
                    'status': member.get_status_display(),
                    'target': {
                        'id': target_id,
                        'name': target.name,
                    }
                })
            message = 'Joined subchannel successfully' if target.open else 'Subchannel join request sent'

        elif target_type == 'group':
            status_value = 1 if target.open else 0  # 1 for Active, 0 for Requested
            group_member, created = SubChannelGroupMembers.objects.get_or_create(group=target, user=user)
            if target_action == 'following':
                group_member.status = 8 if group_member.status == 7 else 7
            elif target_action == 'connecting':
                group_member.status = 11 if group_member.status == 10 else (10 if not target.open else group_member.status)
            group_member.save()
            message = 'Joined group successfully' if target.open else 'Group join request sent'
        
        else:
            return Response({'error': 'Invalid target type'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'memberships': membership_data, 'message': message}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        data = request.query_params
        target_type = data.get('target_type')
        user = request.user

        if not target_type:
            return Response({'error': 'target_type is required'}, status=status.HTTP_400_BAD_REQUEST)

        serializer_class = self.get_serializer_class(target_type)
        if serializer_class is None:
            return Response({'error': 'Invalid target type'}, status=status.HTTP_400_BAD_REQUEST)

        if target_type == 'channel':
            memberships = ChannelMembers.objects.filter(user=user)
        elif target_type == 'subchannel':
            memberships = SubChannelMembers.objects.filter(user=user)
        elif target_type == 'group':
            memberships = SubChannelGroupMembers.objects.filter(user=user)
        else:
            return Response({'error': 'Invalid target type'}, status=status.HTTP_400_BAD_REQUEST)

        membership_data = []
        for membership in memberships:
            if target_type == 'channel':
                target_id = membership.channel.id
                target_name = membership.channel.name
            elif target_type == 'subchannel':
                target_id = membership.sub_channel.id
                target_name = membership.sub_channel.name
            elif target_type == 'group':
                target_id = membership.group.id
                target_name = membership.group.name

            membership_data.append({
                'id': membership.id,
                'status': membership.get_status_display(),
                'target': {
                    'id': target_id,
                    'name': target_name,
                }
            })

        return Response({'memberships': membership_data}, status=status.HTTP_200_OK)
    



class InviteLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, channel_id):
        try:
            channel = Channel.objects.get(id=channel_id)
            invite_link, created = InviteLink.objects.get_or_create(channel=channel)
            serializer = InviteLinkSerializer(invite_link)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Channel.DoesNotExist:
            return Response({"detail": "Channel not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, channel_id):
        try:
            channel = Channel.objects.get(id=channel_id)
            # Delete the existing invite link if it exists
            InviteLink.objects.filter(channel=channel).delete()
            invite_link = InviteLink.objects.create(channel=channel)
            serializer = InviteLinkSerializer(invite_link)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Channel.DoesNotExist:
            return Response({"detail": "Channel not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, channel_id):
        try:
            channel = Channel.objects.get(id=channel_id)
            invite_link, created = InviteLink.objects.get_or_create(channel=channel)
            invite_link.token = uuid.uuid4()  # Regenerate the invite link token
            invite_link.save()
            serializer = InviteLinkSerializer(invite_link)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Channel.DoesNotExist:
            return Response({"detail": "Channel not found"}, status=status.HTTP_404_NOT_FOUND)