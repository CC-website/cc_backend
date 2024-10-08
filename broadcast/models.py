from django.db import models
from django.utils import timezone
from datetime import timedelta

from user.models import User


# Create your models here.
from datetime import timedelta
from django.utils import timezone

class Broadcast(models.Model):
    BROADCAST_TYPES = [
        ('event', 'Event'),
        ('story', 'Story'),
        ('lesson', 'Lesson'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=20, choices=BROADCAST_TYPES)
    content_id = models.PositiveIntegerField()  # Store the ID of the broadcasted item
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    closed_at = models.DateTimeField(blank=True, null=True)  # Make this field optional initially
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Ensure created_at is set before calculating closed_at
        if not self.closed_at and not self.pk:  # Only set closed_at for new instances
            self.created_at = timezone.now()  # Set the created_at timestamp
            self.closed_at = self.created_at + timedelta(days=3)
        elif not self.closed_at:  # If created_at is already set, just update closed_at
            self.closed_at = self.created_at + timedelta(days=3)

        super().save(*args, **kwargs)

    def close_broadcast(self):
        self.is_active = False
        self.save()

    def is_expired(self):
        return timezone.now() > self.closed_at
