from django.db import models

from community.models import Channel

# Create your models here.


class Events(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        CANCELLED = 'CANCELLED', 'Cancelled'
        COMPLETED = 'COMPLETED', 'Completed'
        POSTPONED = 'POSTPONED', 'Postponed'
        DRAFT = 'DRAFT', 'Draft'

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True, choices=[('free', 'Free'), ('paid', 'Paid')])
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    eventPaymentLink = models.CharField(max_length=255, null=True, blank=True)
    paymentMethod = models.CharField(max_length=50, null=True, blank=True)
    allowJoinChannel = models.BooleanField(default=False)
    requireForm = models.BooleanField(default=False)  # Attendee form
    requireAttendeeForm = models.BooleanField(default=False)  # Form for joining the channel
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='event_channel')

    def __str__(self):
        return self.name


class FormQuestion(models.Model):
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('structural', 'Structural'),
        ('essay', 'Essay'),
    ]
    event = models.ForeignKey(Events, related_name='formQuestions', on_delete=models.CASCADE)  # For attendees
    question = models.TextField(blank=True)
    type = models.CharField(max_length=50, choices=QUESTION_TYPES)
    wordLimit = models.CharField(max_length=255, blank=True)
    correctOption = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.question


class FormQuestion2(models.Model):
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('structural', 'Structural'),
        ('essay', 'Essay'),
    ]
    event = models.ForeignKey(Events, related_name='formQuestions2', on_delete=models.CASCADE)  # For those joining the channel
    question = models.TextField(blank=True)
    type = models.CharField(max_length=50, choices=QUESTION_TYPES)
    wordLimit = models.CharField(max_length=255, blank=True)
    correctOption = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.question


class FormOption(models.Model):
    question = models.ForeignKey(FormQuestion, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class FormOption2(models.Model):
    question = models.ForeignKey(FormQuestion2, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text
