from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator

class User(AbstractUser):
    email = models.EmailField(null=True, blank=True)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)

    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default_profile.png')
    facial_recognition_image = models.ImageField(upload_to='facial_recognition_images/', null=True, blank=True)
    about = models.TextField(default='I am on CC!')
    status = models.CharField(max_length=255, default="Available")
    last_seen = models.DateTimeField(blank=True, null=True)

    code = models.JSONField(default=dict, blank=True, null=True)
    contact_list = models.JSONField(default=dict)
    device_tokens = models.JSONField(default=dict)
    settings = models.JSONField(default=dict)
    blocked_users = models.JSONField(default=dict)

    groups = models.ManyToManyField(Group, verbose_name='groups', blank=True, related_name='user_groups')
    user_permissions = models.ManyToManyField(Permission, verbose_name='user permissions', blank=True, related_name='user_permissions')

    def save(self, *args, **kwargs):
        if self.code:
            self.country_code = self.code.get('callingCode', '')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username



class Skill(models.Model):
    user = models.ForeignKey(User, related_name='skills', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    percentage = models.CharField(max_length=10)
    skill_type = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.percentage} ({self.skill_type})"


class Certificate(models.Model):
    user = models.ForeignKey(User, related_name='certificates', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    issued_by = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    media = models.FileField(upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.issued_by} ({self.start_date} to {self.end_date})"


class Education(models.Model):
    user = models.ForeignKey(User, related_name='education', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field = models.CharField(max_length=255)
    description = models.TextField()
    lectures = models.TextField(blank=True, null=True)
    mentors = models.TextField(blank=True, null=True)
    grades = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    media = models.FileField(upload_to='education/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.degree} ({self.start_date} to {self.end_date})"


class Experience(models.Model):
    user = models.ForeignKey(User, related_name='experience', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    employment_type = models.CharField(max_length=100)
    where_found = models.CharField(max_length=100, blank=True)
    is_current = models.BooleanField(default=False)
    media = models.FileField(upload_to='experience/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.position} at {self.company} ({self.start_date} to {self.end_date})"


class Project(models.Model):
    user = models.ForeignKey(User, related_name='projects', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    contributors = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    media = models.FileField(upload_to='projects/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.company} ({self.start_date} to {self.end_date})"


class Service(models.Model):
    user = models.ForeignKey(User, related_name='services', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    media = models.FileField(upload_to='services/', blank=True, null=True)
    where_found = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.name} - {self.user.username} ({self.start_date} to {self.end_date})"
