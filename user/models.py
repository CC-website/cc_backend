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
    about = models.TextField(default='I am on CC!')

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

class PrivacySettings(models.Model):
    PRIVACY_CHOICES = [
        (0, 'Everyone'),
        (1, 'MyContacts'),
        (2, 'MyContactsExcept'),
        (3, 'Nobody'),
    ]

    DISAPPEARING_MESSAGES = [
        (24, '24 hours'),
        (7, '7 days'),
        (30, '30 days'),
        (90, '90 days'),
        (0, 'off'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='privacy_settings')
    last_seen_online = models.IntegerField(choices=PRIVACY_CHOICES, default=0)
    profile_photo = models.IntegerField(choices=PRIVACY_CHOICES, default=0)
    about = models.IntegerField(choices=PRIVACY_CHOICES, default=0)
    status = models.IntegerField(choices=PRIVACY_CHOICES, default=0)
    groups = models.BooleanField(default=False)
    calls = models.IntegerField(choices=PRIVACY_CHOICES, default=0)
    disappearing_messages = models.IntegerField(choices=DISAPPEARING_MESSAGES, default=0)

    def __str__(self):
        return f"Privacy settings for {self.user.username}"
    
class PrivacyExceptions(models.Model):
    privacy = models.ForeignKey(PrivacySettings, on_delete=models.CASCADE, related_name='privacy_exceptions')
    privacy_type = models.CharField(max_length=100, null=True)
    exceptions = models.ManyToManyField(User, related_name='privacy_exceptions', blank=True)

class Wallpaper(models.Model):
    light = models.BooleanField(default=True)
    darck = models.IntegerField(null=True)
    profile_picture = models.ImageField(upload_to='wallpaper/', null=True)
    default = models.BooleanField(default=True)

class Backup(models.Model):
    FREQUENCY = [
        (0, 'Never'),
        (1, 'Only_when_I_tap'),
        (2, 'Daily'),
        (3, 'Weekly'),
        (4, 'Monthly'),
    ]

    frequency = models.IntegerField(choices=FREQUENCY, default=1)
    include_videos = models.BooleanField(default=True)
    cellula = models.BooleanField(default=True)
    end_to_end = models.BooleanField(default=True)
    



class ChatSettings(models.Model):
    THEME = [
        (0, 'Default'),
        (1, 'Light'),
        (2, 'Dark'),
    ]

    FONTsIZE = [
        (0, 'Small'),
        (1, 'Medium'),
        (2, 'Larg'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ChatSettings')
    theme = models.IntegerField(choices=THEME, default=0)
    wallpaper = models.ForeignKey(Wallpaper, related_name='wallpaper', on_delete=models.CASCADE)
    enter = models.BooleanField(default=False)
    media = models.BooleanField(default=True)
    Font_size = models.IntegerField(choices=FONTsIZE, default=1)
    archived = models.BooleanField(default=True)
    backup = models.ForeignKey(Backup, related_name='backup', on_delete=models.CASCADE)
    archive_all_chats = models.BooleanField(default=True)

    def __str__(self):
        return f"Privacy settings for {self.user.username}"