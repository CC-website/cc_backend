from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action

from broadcast.models import Broadcast
from event.models import Events
import json
from event.serializers import EventSerializer

# Create your views here.
    
class EventViewSet(viewsets.ModelViewSet):
    queryset = Events.objects.all()  # Fetch all events
    serializer_class = EventSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        # Extract event data from request
        event_data = request.data.get('eventData', None)

        # Log the uploaded image for debugging
        print("Uploaded image:", request.FILES.get('image'))

        # If event_data is a JSON string, parse it into a Python dictionary
        if isinstance(event_data, str):
            try:
                event_data = json.loads(event_data)  # Load JSON data
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format."}, status=status.HTTP_400_BAD_REQUEST)

        # Add image file to event data if available
        if request.FILES.get('image'):
            event_data['image'] = request.FILES.get('image')

        # Serialize the data
        serializer = EventSerializer(data=event_data)
        if serializer.is_valid():
            event = serializer.save()  # Save event with image and other data
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, *args, **kwargs):
        # Retrieve and handle event data from the request
        event_data = request.data.get('eventData')
        
        if event_data:
            try:
                # Safely convert stringified JSON into Python dict
                event_data = json.loads(event_data)
                request.data.update(event_data)
            except json.JSONDecodeError as e:
                return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)

        # If there's an image file uploaded, make sure it's handled correctly
        if 'image' in request.FILES:
            request.data['image'] = request.FILES['image']

        # Call the superclass update method
        return super().update(request, *args, **kwargs)



    def list(self, request, *args, **kwargs):
        # Retrieve the channel_id from the query parameters
        channel_id = request.query_params.get('channel_id')

        # Filter the queryset based on the channel_id if it exists
        if channel_id:
            queryset = Events.objects.filter(channel_id=channel_id)
        else:
            queryset = Events.objects.all()

        # Retrieve all broadcasts for the events in the queryset to avoid repeated database queries
        broadcast_ids = set(Broadcast.objects.filter(content_type='event', content_id__in=queryset.values_list('id', flat=True), is_active=True).values_list('content_id', flat=True))

        events = []
        for event in queryset:
            event_data = {
                'id': event.id,
                'name': event.name,
                'description': event.description,
                'date': event.date,
                'type': event.type,
                'price': 'Free' if event.type != 'paid' else event.price,
                'status': event.status,
                'allowJoinChannel': event.allowJoinChannel,
                'requireForm': event.requireForm,
                'requireAttendeeForm': event.requireAttendeeForm,
                'image': event.image.url if event.image else None,
                'eventPaymentLink': event.eventPaymentLink,
                'paymentMethod': event.paymentMethod,
                'broadcast': event.id in broadcast_ids,
            }
            events.append(event_data)


        return Response(events, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        # Get the event instance
        event = self.get_object()

        # Retrieve all broadcasts for the event to avoid repeated database queries
        is_broadcasted = Broadcast.objects.filter(content_type='event', content_id=event.id, is_active=True).exists()

        # Prepare event data
        event_data = {
            'id': event.id,
            'name': event.name,
            'description': event.description,
            'date': event.date,
            'type': event.type,
            'price': 'Free' if event.type != 'paid' else event.price,
            'allowJoinChannel': event.allowJoinChannel,
            'requireForm': event.requireForm,
            'requireAttendeeForm': event.requireAttendeeForm,
            'image': event.image.url if event.image else None,
            'eventPaymentLink': event.eventPaymentLink,
            'paymentMethod': event.paymentMethod,
            'broadcast': is_broadcasted,
            'formQuestions': [
                {
                    'id': question.id,
                    'question': question.question,
                    'type': question.type,
                    'wordLimit': question.wordLimit,
                    'correctOption': question.correctOption,
                    'options': [{'id': option.id, 'text': option.text} for option in question.options.all()]
                }
                for question in event.formQuestions.all()
            ],
            'formQuestions2': [
                {
                    'id': question.id,
                    'question': question.question,
                    'type': question.type,
                    'wordLimit': question.wordLimit,
                    'correctOption': question.correctOption,
                    'options': [{'id': option.id, 'text': option.text} for option in question.options.all()]
                }
                for question in event.formQuestions2.all()
            ],
        }

        return Response(event_data, status=status.HTTP_200_OK)

    # Custom action to update event status
    @action(detail=True, methods=['GET'], url_path='update-status')
    def update_status(self, request, pk=None):
        event = self.get_object()  # Retrieve the event based on the provided 'pk'
        new_status = request.query_params.get('status')  # Get the new status from query parameters

        # Check if the new status is provided
        if not new_status:
            return Response({"detail": "Status is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the provided status is valid
        if new_status not in [choice[0] for choice in Events.Status.choices]:
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Update the event status
            event.status = new_status
            event.save()

            return Response({"detail": f"Event status changed to {new_status} successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
