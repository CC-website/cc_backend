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

from user.models import User
from user.serializers import UserSerializer
from .models import Channel, Permission, PermissionAssignment, SubChannel, Group

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Channel
from .serializers import ChannelSerializer, ChannelSerializer2, PermissionAssignmentSerializer, PermissionSerializer, SubChannelSerializer, SubGroupSerializer
from rest_framework.parsers import MultiPartParser, FormParser
import json
from django.views.decorators.http import require_POST
import base64
from django.core.files.base import ContentFile

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q




class ChannelPermissionCheckerView(View):
    def get_user_permissions(self, user):

        # Fetch channels where the user is an owner, admin, or member
        channels = Channel.objects.filter(Q(owner=user) | Q(admins=user) | Q(members=user))
        
        if channels:
            user_permissions_dict = {}
            
            for channel in channels:
                # Determine permission type for the user
                if channel.owner == user:
                    permission_type = 'admin'
                elif user in channel.admins.all():
                    permission_type = 'admin'
                elif user in channel.members.all():
                    permission_type = 'member'
                else:
                    continue  # Skip to the next channel if the user is not associated with it
                
                # Retrieve permission assignments for the channel and user
                permission_assignments = PermissionAssignment.objects.filter(target_id=channel.id, target_type='channel', permission_type=permission_type)

                user_channel_permissions = []
                if(channel.owner):
                    user_channel_permissions.append({
                        'permissions': 'owner'
                    })

                # Iterate through permission assignments
                for assignment in permission_assignments:
                    # Check if the user has exception permissions
                    if user not in assignment.permission.first().exception_users.all():
                        # Add permissions to the user_channel_permissions list
                      
                        user_channel_permissions.append({
                            'permissions': assignment.permission.all()
                        })
                        
                        

                # Add the user permissions for the current channel to the user_permissions_dict
                user_permissions_dict[channel.id] = {'user_permissions': user_channel_permissions}

            return user_permissions_dict

        return False

    def get(self, request):
        user = request.user
        user_permissions = self.get_user_permissions(user)

        if user_permissions:
            return JsonResponse(user_permissions)
        else:
            return JsonResponse({'message': 'User does not have permissions for any channel.'}, status=404)





class SubChannelPermissionCheckerView(View):
    def get_user_permissions(self, user):
        # Fetch subchannels where the user is an owner, admin, or member
        subchannels = SubChannel.objects.filter(Q(channel__owner=user) | Q(admins=user) | Q(members=user))

        if subchannels:
            user_permissions_dict = {}
            
            for subchannel in subchannels:
                # Determine permission type for the user
                if subchannel.channel.owner == user:
                    permission_type = 'admin'
                elif user in subchannel.admins.all():
                    permission_type = 'admin'
                elif user in subchannel.members.all():
                    permission_type = 'member'
                else:
                    continue  # Skip to the next subchannel if the user is not associated with it
                
                # Retrieve permission assignments for the subchannel and user
                permission_assignments = PermissionAssignment.objects.filter(target_id=subchannel.id, target_type='subchannel', permission_type=permission_type)

                user_subchannel_permissions = []

                # Iterate through permission assignments
                for assignment in permission_assignments:
                    # Check if the user has exception permissions
                    if user not in assignment.permission.first().exception_users.all():
                        # Add permissions to the user_subchannel_permissions list
                        user_subchannel_permissions.append({
                            'permissions': assignment.permission.all()
                        })

                # Add the user permissions for the current subchannel to the user_permissions_dict
                user_permissions_dict[subchannel.id] = {'user_permissions': user_subchannel_permissions}

            return user_permissions_dict

        return False

    def get(self, request):
        user = request.user
        user_permissions = self.get_user_permissions(user)

        if user_permissions:
            return JsonResponse(user_permissions)
        else:
            return JsonResponse({'message': 'User does not have permissions for any subchannel.'}, status=404)


class GroupPermissionCheckerView(View):
    def get_user_permissions(self, user):
        # Fetch groups where the user is an owner, admin, or member
        groups = Group.objects.filter(Q(subchannel__channel__owner=user) | Q(admins=user) | Q(members=user))

        if groups:
            user_permissions_dict = {}
            
            for group in groups:
                # Determine permission type for the user
                if group.subchannel.channel.owner == user:
                    permission_type = 'admin'
                elif user in group.admins.all():
                    permission_type = 'admin'
                elif user in group.members.all():
                    permission_type = 'member'
                else:
                    continue  # Skip to the next group if the user is not associated with it
                
                # Retrieve permission assignments for the group and user
                permission_assignments = PermissionAssignment.objects.filter(target_id=group.id, target_type='group', permission_type=permission_type)

                user_group_permissions = []

                # Iterate through permission assignments
                for assignment in permission_assignments:
                    # Check if the user has exception permissions
                    if user not in assignment.permission.first().exception_users.all():
                        # Add permissions to the user_group_permissions list
                        user_group_permissions.append({
                            'permissions': assignment.permission.all()
                        })

                # Add the user permissions for the current group to the user_permissions_dict
                user_permissions_dict[group.id] = {'user_permissions': user_group_permissions}

            return user_permissions_dict

        return False

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
            data = {'owner':user.id, 'name': name, 'description': description, 'logo':image_data }
            
            serializer = ChannelSerializer(data=data)
            
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
            
            # Fetch channels where the user has permissions
            print(channel_permissions)
            if channel_permissions:
                channels = Channel.objects.filter(id__in=channel_permissions.keys())

                # Serialize channels
                for channel in channels:
                    channel_data = model_to_dict(channel, fields=['id', 'name', 'description'])
                    channel_data['image_url'] = request.build_absolute_uri(channel.logo.url) if channel.logo else None
                    channel_data['subchannels'] = []

                    # Check if there are subchannel permissions for this channel
                    
                    if subchannel_permissions:
                        # Fetch subchannels where the user has permissions
                        subchannels = SubChannel.objects.filter(channel=channel, id__in=subchannel_permissions.keys())
                        
                        # Serialize subchannels
                        for subchannel in subchannels:
                            subchannel_data = model_to_dict(subchannel, fields=['id', 'name', 'description'])
                            subchannel_data['image_url'] = request.build_absolute_uri(subchannel.logo.url) if subchannel.logo else None
                            subchannel_data['groups'] = []

                            # Check if there are group permissions for this subchannel
                            if group_permissions:
                                # Fetch groups where the user has permissions
                                groups = Group.objects.filter(subchannel=subchannel, id__in=group_permissions.keys())

                                # Serialize groups
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
            
            
            user = User.objects.filter(id=request.user.id).first()

            if name is not None:
                channel.name = name
            if description is not None:
                channel.description = description
            if user.id is not None:
                channel.id = user.id
            if image_data is not None:
                channel.logo = image_data

            channel.save()
            serializer = ChannelSerializer(channel)
            response = serializer.data
            print(response)
            return Response(response, status=200)

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
        


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

    def get_members(self, request, pk=None):
        channel = self.get_object()
        members = channel.members.all()
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)
    
    def get_admins(self, request, pk=None):
        channel = self.get_object()
        members = channel.admins.all()
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)
    
    def get_blocked_members(self, request, pk=None):
        channel = self.get_object()
        members = channel.blocked_members.all()
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)

    def move_to_admins(self, request, pk=None):
        channel = self.get_object()
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        channel.members.remove(user)
        channel.admins.add(user)
        return Response(status=status.HTTP_200_OK)

    def move_to_blocked_members(self, request, pk=None):
        channel = self.get_object()
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        channel.members.remove(user)
        channel.blocked_members.add(user)
        return Response(status=status.HTTP_200_OK)

    def delete_member(self, request, pk=None):
        channel = self.get_object()
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        channel.members.remove(user)
        channel.admins.remove(user)
        channel.blocked_members.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def move_from_blocked_members(self, request, pk=None):
        channel = self.get_object()
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        channel.blocked_members.remove(user)
        channel.members.add(user)
        return Response(status=status.HTTP_200_OK)
    
    def move_from_admins(self, request, pk=None):
        channel = self.get_object()
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        channel.admins.remove(user)
        channel.members.add(user)
        return Response(status=status.HTTP_200_OK)
    

class PermissionTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class PermissionAssignmentAPIView(APIView):

    def get(self, request, target_id, target_type):
        roles = PermissionAssignment.objects.filter(target_type=target_type, target_id=target_id)
        data = []
        if roles:
            for role in roles:
                serializer = PermissionAssignmentSerializer(role)
                permissions = serializer.data['permission']
                permission_array = []
                for permission in permissions:
                    permission_data = Permission.objects.filter(pk=permission).first()
                    if permission_data:
                        permission_array.append(PermissionSerializer(permission_data).data['permission_type'])
                
                updated_data = serializer.data.copy()  # Create a copy of serializer.data
                updated_data['permission'] = permission_array  # Update the permission field
                data.append(updated_data)  # Append the updated copy to data

            return Response(data)
        
        return Response({'message': 'No roles available'})

    def post(self, request):
        serializer = PermissionAssignmentSerializer(data=request.data)
        print("Nigel")
        
        if serializer.is_valid():
            print("Nigel Bah")
            permission_data = request.data
            permissions_ids = permission_data.pop('permission', [])
            members_ids = permission_data.pop('members', [])
            
            # Check if the assignment already exists
            existing_assignment = PermissionAssignment.objects.filter(
                permission__in=permissions_ids,
                members__in = members_ids,
                permission_type=permission_data['permission_type'],
                target_id=permission_data['target_id'],
                target_type=permission_data['target_type']
            ).exists()
            
            if existing_assignment:
                return Response({'error': 'Assignment already exists.'})

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request):
        try:
            permission_assignment_id = request.data.get('permission_assignment_id')
            permission_assignment = PermissionAssignment.objects.get(pk=permission_assignment_id)

            # If permissions_updates are provided, replace the existing permissions
            if 'permissions_updates' in request.data:
                permission_data = request.data.get('permissions_updates')
                new_permission_ids = [data['id'] for data in permission_data]
                
                # Clear existing permissions
                permission_assignment.permission.clear()
                
                # Add new permissions
                permission_assignment.permission.add(*new_permission_ids)

            elif 'permissions_update_members' in request.data:
                member_data = request.data.get('permissions_update_members')
                new_member_ids =  member_data
                
                # Clear existing permissions
                permission_assignment.members.clear()
                
                # Add new permissions
                permission_assignment.members.add(*new_member_ids)
            else:
                # Update permission_type and all_users if provided
                permission_type = request.data.get('permission_type')
                all_users = request.data.get('all_users')
                permission_assignment.permission_type = permission_type
                permission_assignment.all_members = all_users
            
            # Save the changes
            permission_assignment.save()
            
            # Serialize the updated instance
            serializer = PermissionAssignmentSerializer(permission_assignment)
            
            # Return the serialized data in the response
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except PermissionAssignment.DoesNotExist:
            return Response({"error": "PermissionAssignment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class PermissionAssignmentListView(generics.ListAPIView):
    serializer_class = PermissionAssignmentSerializer

    def get_queryset(self):
        user_ids = self.request.query_params.getlist('user_ids[]', [])  # Get user IDs from query parameters
        print(user_ids)
        target_id = self.request.query_params.get('target_id')  # Get target ID from query parameters
        queryset = PermissionAssignment.objects.filter(members__id__in=user_ids, target_id=target_id)
        return queryset
    
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
        channel = get_object_or_404(Channel, pk=channel_id)
        user_id = request.data.get('user_id')
        if action != 'restore':
            user = get_object_or_404(User, pk=user_id) 
        
        if action == 'band':
            channel.members.remove(user)
            channel.blocked_members.add(user)
            print(channel.blocked_members.get())

        elif action == 'kick':
            channel.members.remove(user)

        elif action == 'transfer':
            channel.owner = user
            channel.save()
            channel.members.add(user)
        
        elif action == 'restore':
            for data in user_id:
                user = get_object_or_404(User, pk=data) 
                channel.blocked_members.remove(user)
                channel.members.add(user)
        
        return Response({'message': 'User Status has been updated'}, status=status.HTTP_200_OK)



class GetBanedMembers(APIView):

    def get(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        serializer = ChannelSerializer2(channel)
        return Response(serializer.data, status=status.HTTP_200_OK)