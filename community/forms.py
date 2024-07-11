# forms.py

from django import forms
from .models import Channel, SubChannel, Group

class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ['name', 'logo', 'description']

class SubChannelForm(forms.ModelForm):
    class Meta:
        model = SubChannel
        fields = ['channel', 'name', 'logo', 'description']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['subchannel', 'name', 'logo', 'description']
