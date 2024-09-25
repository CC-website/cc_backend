from rest_framework import generics, permissions

from user.models import Message, User
from .models import GroupChat, SignalKey
from .serializers import MessageSerializer, GroupChatSerializer
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status

# views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def exchange_keys(request):
    if request.method == 'POST':
        user = request.user
        identity_key = request.POST.get('identity_key')
        signed_pre_key = request.POST.get('signed_pre_key')
        pre_key = request.POST.get('pre_key')

        SignalKey.objects.update_or_create(
            user=user,
            defaults={'identity_key': identity_key, 'signed_pre_key': signed_pre_key, 'pre_key': pre_key}
        )
        return JsonResponse({'status': 'success'})

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        sender = request.user
        receiver_id = request.POST.get('receiver_id')
        plaintext = request.POST.get('message')
        
        receiver = get_object_or_404(User, pk=receiver_id)
        receiver_keys = get_object_or_404(SignalKey, user=receiver)
        
        ciphertext =  plaintext
        
        Message.objects.create(sender=sender, receiver=receiver, ciphertext=ciphertext)
        
        return JsonResponse({'status': 'success'})

@csrf_exempt
def fetch_messages(request):
    if request.method == 'GET':
        user = request.user
        messages = Message.objects.filter(receiver=user)
        decrypted_messages = [
            {
                'sender': msg.sender.username,
                'message': msg.ciphertext,
                'timestamp': msg.timestamp
            } for msg in messages
        ]
        
        return JsonResponse({'messages': decrypted_messages})



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
