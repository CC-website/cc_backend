# models.py

from django.db import models

class Channel(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='channel_logos/', null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class SubChannel(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='subchannel_logos/', null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class Group(models.Model):
    subchannel = models.ForeignKey(SubChannel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='group_logos/', null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.name
