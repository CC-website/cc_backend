from rest_framework import generics, permissions

from user.models import User
from .models import Message, GroupChat
from .serializers import MessageSerializer, GroupChatSerializer
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status


class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()  # Make a copy of request data to modify it safely
        user = request.user  # Assuming request.user is the authenticated user object
        
        # Add user to data dictionary
        data['user'] = user.id  # Assuming 'user' field in Message model expects user's id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # Instead of serializer.save(), use serializer.create() to handle object creation
        instance = serializer.create(serializer.validated_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupChatListCreateView(generics.ListCreateAPIView):
    queryset = GroupChat.objects.all()
    serializer_class = GroupChatSerializer
    permission_classes = [permissions.IsAuthenticated]
