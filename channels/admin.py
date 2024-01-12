# admin.py

from django.contrib import admin
from .models import Channel, SubChannel, Group

admin.site.register(Channel)
admin.site.register(SubChannel)
admin.site.register(Group)
