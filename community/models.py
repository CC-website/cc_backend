from django.db import models
import uuid
import random

class Permission(models.Model):
    PERMISSION_CHOICES = [
        (0, 'Update Community'),
        (1, 'Add Members'),
        (2, 'Grant Sub-community Access'),
        (3, 'Ban Members'),
        (4, 'Remove Members'),
        (5, 'Create Sub-communities'),
        (6, 'Update Sub-communities'),
        (7, 'Delete Sub-communities'),
        (8, 'Create Groups'),
        (9, 'Update Groups'),
        (10, 'Delete Groups'),
        (11, 'Grant Group Access'),
        (12, 'Create Community Roles'),
        (13, 'Create Sub-community Roles'),
        (14, 'Create Group Roles'),
        (15, 'Mute Members'),
        (16, 'Set Group Messaging Status'),
    ]

    TARGET_TYPE_CHOICES = [
        ('community', 'Community'),
        ('sub-community', 'Sub-community'),
        ('group', 'Group'),
    ]

    permission_type = models.IntegerField(choices=PERMISSION_CHOICES)
    target_type = models.CharField(max_length=20, null=True, blank=True, choices=TARGET_TYPE_CHOICES)

    def __str__(self):
        return f'Permission ID: {self.id} - Type: {self.get_permission_type_display()}'



class PermissionAssignment(models.Model):
    permission = models.ManyToManyField(Permission)
    permission_type = models.CharField(default="member", max_length=120)
    target_id = models.IntegerField() 
    target_type = models.CharField(max_length=20)
    all_members = models.BooleanField(default=False) 

    def __str__(self):
        return f'{self.permission_type.capitalize()} Permission for {self.target_type.capitalize()} ID: {self.target_id}'

class Channel(models.Model):
    owner = models.ForeignKey('user.User', null=True, on_delete=models.CASCADE, related_name='user_channels')
    Original_owner = models.ForeignKey('user.User', null=True, on_delete=models.CASCADE, related_name='original_owner', blank=True)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='channel_logos/', null=True, blank=True)
    description = models.TextField()
    connect_link = models.TextField(null=True, blank=True)
    open = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ChannelMembers(models.Model):
    STATUS = [
        (0, 'Requested'),
        (1, 'Active'),
        (2, 'Inactive'),
        (3, 'Suspended'),
        (4, 'Admitted'),
        (5, 'Blocked'),
        (6, 'Removed'),
        (7, 'Following'),
        (8, 'Un-followed'),
        (9, 'Inactive'),
        (10, 'Connected'),
        (11, 'Disconnected'),
    ]

    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='channel_member')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='this_channel_member')
    type = models.JSONField(default=list, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True, choices=STATUS)

    def __str__(self):
        return f"{self.user} in {self.channel} - Status: {self.get_status_display()}"
    
    

class MFA(models.Model):
    code = models.CharField(max_length=6, unique=True)
    channel = models.OneToOneField(Channel, on_delete=models.CASCADE, related_name='mfa')
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        self.code = f"{random.randint(100000, 999999)}"
        self.save()

    def __str__(self):
        return f"MFA Code for Channel: {self.channel.name} - Code: {self.code}"


class SubChannel(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='subchannels')
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='subchannel_logos/', null=True, blank=True)
    description = models.TextField()
    connect_link = models.TextField(null=True, blank=True)
    open = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SubChannelMembers(models.Model):
    STATUS = [
        (0, 'Requested'),
        (1, 'Active'),
        (2, 'Inactive'),
        (3, 'Suspended'),
        (4, 'Admitted'),
        (5, 'Blocked'),
        (6, 'Removed'),
        (7, 'Following'),
        (8, 'Un-followed'),
        (9, 'Inactive'),
        (10, 'Connected'),
        (11, 'Disconnected'),
    ]

    sub_channel = models.ForeignKey(SubChannel, on_delete=models.CASCADE, related_name='sub_channel_member')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='this_sub_channel_member')
    type = models.JSONField(default=list, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True, choices=STATUS)

    def __str__(self):
        return f"{self.user} in {self.sub_channel} - Status: {self.get_status_display()}"


class Group(models.Model):
    subchannel = models.ForeignKey(SubChannel, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='group_logos/', null=True, blank=True)
    description = models.TextField()
    connect_link = models.TextField(null=True, blank=True)
    open = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class SubChannelGroupMembers(models.Model):
    STATUS = [
        (0, 'Requested'),
        (1, 'Active'),
        (2, 'Inactive'),
        (3, 'Suspended'),
        (4, 'Amitted'),
        (5, 'Blocked'),
        (6, 'Removed'),
        (7, 'Following'),
        (8, 'Un-followed'),
        (9, 'Inactive'),
        (10, 'connected'),
        (11, 'disconnected'),
    ]
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='sub_channel_group_member')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='this_sub_channel_group_member')
    type = models.TextField(null=True, blank=True)
    status = models.IntegerField(blank=True, null=True, choices=STATUS)


class InviteLink(models.Model):
    channel = models.OneToOneField(Channel, on_delete=models.CASCADE, related_name='invite_link')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Invite link for channel: {self.channel.name}'