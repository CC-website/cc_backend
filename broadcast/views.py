from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Broadcast
from .serializers import BroadcastSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers  
from rest_framework.decorators import action

class BroadcastViewSet(viewsets.ModelViewSet):
    queryset = Broadcast.objects.all()
    serializer_class = BroadcastSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        content_type = serializer.validated_data.get('content_type')
        content_id = serializer.validated_data.get('content_id')

        # Check if a broadcast with the same content_type and content_id already exists
        if Broadcast.objects.filter(content_type=content_type, content_id=content_id).exists():
            raise serializers.ValidationError("A broadcast with this content type and content ID already exists.")
        
        # Save the broadcast with the logged-in user
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get query parameters for filtering
        content_type = self.request.query_params.get('content_type')
        content_id = self.request.query_params.get('content_id')

        # Apply filtering based on content_type and content_id if provided
        if content_type and content_id:
            queryset = queryset.filter(content_type=content_type, content_id=content_id)
        elif content_type:
            queryset = queryset.filter(content_type=content_type)

        return queryset

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_expired():
            return Response({"detail": "Cannot update, the broadcast has expired."}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def close(self, request):
        content_type = request.data.get('content_type')
        content_id = request.data.get('content_id')

        # Validate that both content_type and content_id are provided
        if not content_type or not content_id:
            return Response({"detail": "Both content_type and content_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the broadcast based on content_type and content_id
        broadcast = Broadcast.objects.filter(content_type=content_type, content_id=content_id).first()

        if broadcast:
            if broadcast.is_active:
                # Close the broadcast if it's active
                broadcast.close_broadcast()
                return Response({
                    "detail": "Broadcast closed successfully.",
                    "broadcast": broadcast.is_active  # Include the updated status of the broadcast
                }, status=status.HTTP_200_OK)
            else:
                # Reopen the broadcast if it's inactive
                broadcast.is_active = True
                broadcast.save()
                return Response({
                    "detail": "Broadcast opened successfully.",
                    "broadcast": broadcast.is_active  # Include the updated status of the broadcast
                }, status=status.HTTP_200_OK)

        else:
            # If no broadcast exists, create a new one
            broadcast = Broadcast.objects.create(
                user=request.user,
                content_type=content_type,
                content_id=content_id,
                is_active=True  # Mark as active when creating a new broadcast
            )
            return Response({
                "detail": "Broadcast opened successfully.",
                "broadcast": broadcast.is_active  # Include the updated status of the broadcast
            }, status=status.HTTP_200_OK)

