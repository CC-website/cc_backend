from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator

class User(AbstractUser):
    email = models.EmailField( null=True, blank=True)
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
    )
    
    code = models.JSONField(default=dict, blank=True, null=True)
    facial_recognition_image = models.ImageField(upload_to='facial_recognition_images/', null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default_profile.png')
    status = models.PositiveSmallIntegerField(default=0)
    last_seen = models.DateTimeField(blank=True, null=True)
    contact_list = models.JSONField(default=dict)
    device_tokens = models.JSONField(default=dict)
    settings = models.JSONField(default=dict)
    blocked_users = models.JSONField(default=dict)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='user_groups'  # Add a unique related_name
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='user_permissions'  # Add a unique related_name
    )

    def save(self, *args, **kwargs):
        # Extract country code information and update the model's country_code field
        if self.code:
            self.country_code = self.code.get('callingCode', '')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
