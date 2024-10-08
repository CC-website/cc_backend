# Serializer for Form Option
from rest_framework import serializers
from event.models import Events, FormOption, FormOption2, FormQuestion, FormQuestion2
import os
import time
from django.utils.text import slugify

class FormOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormOption
        fields = ['id', 'text']

# Serializer for Form Option2
class FormOption2Serializer(serializers.ModelSerializer):
    class Meta:
        model = FormOption2
        fields = ['id', 'text']

# Serializer for Form Question
class FormQuestionSerializer(serializers.ModelSerializer):
    options = FormOptionSerializer(many=True)

    class Meta:
        model = FormQuestion
        fields = ['id', 'question', 'type', 'wordLimit', 'correctOption', 'options', 'event']
        extra_kwargs = {
            'event': {'required': False},
            'options': {'required': False},
            'correctOption': {'required': False},
            'wordLimit': {'required': False},
            'type': {'required': False},
            'question': {'required': False},
        }

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        event = validated_data.pop('event')  # Ensure to pop event from validated_data
        form_question = FormQuestion.objects.create(event=event, **validated_data)  # Pass event to create

        # Create nested options and link them to the form question
        for option_data in options_data:
            FormOption.objects.create(question=form_question, **option_data)

        return form_question

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', [])
        # Update the fields of the FormQuestion instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save the updated instance
        instance.save()

        # Update nested options
        # First, clear existing options
        instance.options.all().delete()

        # Create new options
        for option_data in options_data:
            FormOption.objects.create(question=instance, **option_data)

        return instance



# Serializer for Form Question2
class FormQuestion2Serializer(serializers.ModelSerializer):
    options = FormOption2Serializer(many=True)

    class Meta:
        model = FormQuestion2
        fields = ['id', 'question', 'type', 'wordLimit', 'correctOption', 'options', 'event'] 
        extra_kwargs = {
            'event': {'required': False},
            'options': {'required': False},
            'correctOption': {'required': False},
            'wordLimit': {'required': False},
            'type': {'required': False},
            'question': {'required': False},
        }

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        event = validated_data.pop('event')  # Ensure to pop event from validated_data
        form_question2 = FormQuestion2.objects.create(event=event, **validated_data)  # Pass event to create

        # Create nested options and link them to the form question2
        for option_data in options_data:
            FormOption2.objects.create(question=form_question2, **option_data)

        return form_question2

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', [])
        # Update the fields of the FormQuestion2 instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save the updated instance
        instance.save()

        # Update nested options
        # First, clear existing options
        instance.options.all().delete()

        # Create new options
        for option_data in options_data:
            FormOption2.objects.create(question=instance, **option_data)

        return instance





# Main serializer for Event
class EventSerializer(serializers.ModelSerializer):
    formQuestions = FormQuestionSerializer(many=True, required=False)
    formQuestions2 = FormQuestion2Serializer(many=True, required=False)

    class Meta:
        model = Events
        fields = [
            'id', 'name', 'description', 'date', 'type', 'price', 'status',
            'eventPaymentLink', 'paymentMethod', 'allowJoinChannel',
            'requireForm', 'requireAttendeeForm', 'image', 'channel',
            'formQuestions', 'formQuestions2'
        ]
        extra_kwargs = {
            'image': {'required': False},
            'type': {'required': False},
            'formQuestions': {'required': False},
            'formQuestions2': {'required': False},
            'allowJoinChannel': {'required': False},
            'status': {'required': False},
            'price': {'required': False},  # Make price optional
            'eventPaymentLink': {'required': False},  # Make payment link optional
            'paymentMethod': {'required': False},  # Make payment method optional
            'requireForm': {'required': False},  # Make requireForm optional
            'requireAttendeeForm': {'required': False},  # Make requireAttendeeForm optional
        }

    def create(self, validated_data):
        form_questions_data = validated_data.pop('formQuestions', [])
        form_questions2_data = validated_data.pop('formQuestions2', [])
        image = validated_data.pop('image', None)
        print("Creating Event with formQuestions2:", form_questions2_data)

        try:
            # Create the main event
            event = Events.objects.create(**validated_data)

            # Handle image saving
            if image:
                timestamp = int(time.time())
                base, ext = os.path.splitext(image.name)
                unique_filename = f"{slugify(base)}_{timestamp}{ext}"
                event.image.save(unique_filename, image)
                event.save()

            print("Event created:", event)

            # Save form questions
            for question_data in form_questions_data:
                question_data['event'] = event.id  # Pass the event ID, not the full object
                question_serializer = FormQuestionSerializer(data=question_data)
                if question_serializer.is_valid(raise_exception=True):
                    question_serializer.save()  # This internally calls the create method
                else:
                    print("FormQuestionSerializer validation errors:", question_serializer.errors)

            # Save form questions2
            for question2_data in form_questions2_data:
                question2_data['event'] = event.id  # Pass the event ID, not the full object
                question2_serializer = FormQuestion2Serializer(data=question2_data)
                if question2_serializer.is_valid(raise_exception=True):
                    question2_serializer.save()  # This internally calls the create method
                else:
                    print("FormQuestion2Serializer validation errors:", question2_serializer.errors)

            return event

        except Exception as e:
            print(f"Error creating event: {e}")
            raise e



    def update(self, instance, validated_data):
        # Directly update the instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        print("Now Nigel can see it all from here 0000000000000000000", instance.id)

        # Handle image updates (if new image is provided)
        image = validated_data.get('image', None)
        if image:
            timestamp = int(time.time())
            base, ext = os.path.splitext(image.name)
            unique_filename = f"{slugify(base)}_{timestamp}{ext}"
            instance.image.save(unique_filename, image)

        # Save the main instance with updated fields
        instance.save()

        # Retrieve form questions data from the request
        form_questions_data = self.context['request'].data.get('formQuestions', [])
        form_questions2_data = self.context['request'].data.get('formQuestions2', [])

        print("form_questions_data: ", form_questions_data)
        print("form_questions2_data: ", form_questions2_data)

        # Update form questions (handle delete and add/update)
        instance.formQuestions.all().delete()  # Remove old form questions
        for question_data in form_questions_data:
            question_data['event'] = instance.id  # Associate the event instance
            question_serializer = FormQuestionSerializer(data=question_data)
            if question_serializer.is_valid(raise_exception=True):
                question_serializer.save()  # Save with the associated event

        # Update form questions2 (handle delete and add/update)
        instance.formQuestions2.all().delete()  # Remove old form questions2
        for question2_data in form_questions2_data:
            question2_data['event'] = instance.id  # Associate the event instance
            question2_serializer = FormQuestion2Serializer(data=question2_data)
            if question2_serializer.is_valid(raise_exception=True):
                question2_serializer.save()  # Save with the associated event

        return instance






