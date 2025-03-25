from django.db import models

from user.models import User


class GroupChat(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='group_chats')


class SignalKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    identity_key = models.TextField()
    signed_pre_key = models.TextField()
    pre_key = models.TextField()

