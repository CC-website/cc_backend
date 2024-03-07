from django.db import models

class Permission(models.Model):
    PERMISSION_CHOICES = [
        (0, 'Delete'),
        (1, 'Create'),
        (2, 'Update'),
        (3, 'Is super admin'),
        (4, 'Add member'),
        (5, 'Remove member'),
    ]

    permission_type = models.IntegerField(choices=PERMISSION_CHOICES)
    exception_users = models.ManyToManyField('user.User', related_name='exception_permissions')

    def __str__(self):
        return f'Permission ID: {self.id} - Type: {self.get_permission_type_display()}'

class PermissionAssignment(models.Model):
    permission = models.ManyToManyField(Permission)
    permission_type = models.CharField(max_length=120)
    target_id = models.IntegerField() 
    members = models.ManyToManyField('user.User', related_name='Permission_members')
    target_type = models.CharField(max_length=20)
    all_members = models.BooleanField(default=False) 

    def __str__(self):
        return f'{self.permission_type.capitalize()} Permission for {self.target_type.capitalize()} ID: {self.target_id}'

class Channel(models.Model):
    owner = models.ForeignKey('user.User', null=True, on_delete=models.CASCADE, related_name='user_channels')
    members = models.ManyToManyField('user.User', related_name='channel_members')
    admins = models.ManyToManyField('user.User', related_name='admin_channels')
    blocked_members = models.ManyToManyField('user.User', related_name='blocked_channel_members')
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='channel_logos/', null=True, blank=True)
    description = models.TextField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Set initial permissions for all admins
        admins = self.admins.all()
        for admin in admins:
            permission_assignment = PermissionAssignment.objects.create(permission_type='admin', target_id=self.id, target_type='channel')
            permission_assignment.permission.add(*Permission.objects.all())
            permission_assignment.save()

    def __str__(self):
        return self.name

class SubChannel(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='subchannels')
    members = models.ManyToManyField('user.User', related_name='subchannel_members')
    admins = models.ManyToManyField('user.User', related_name='admin_subchannels')
    blocked_members = models.ManyToManyField('user.User', related_name='blocked_subchannel_members')
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='subchannel_logos/', null=True, blank=True)
    description = models.TextField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Set initial permissions for all admins
        admins = self.admins.all()
        for admin in admins:
            permission_assignment = PermissionAssignment.objects.create(permission_type='admin', target_id=self.id, target_type='subchannel')
            permission_assignment.permission.add(*Permission.objects.all())
            permission_assignment.save()

    def __str__(self):
        return self.name

class Group(models.Model):
    subchannel = models.ForeignKey(SubChannel, on_delete=models.CASCADE, related_name='groups')
    members = models.ManyToManyField('user.User', related_name='group_members')
    admins = models.ManyToManyField('user.User', related_name='admin_groups')
    blocked_members = models.ManyToManyField('user.User', related_name='blocked_group_members')
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='group_logos/', null=True, blank=True)
    description = models.TextField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Set initial permissions for all admins
        admins = self.admins.all()
        for admin in admins:
            permission_assignment = PermissionAssignment.objects.create(permission_type='admin', target_id=self.id, target_type='group')
            permission_assignment.permission.add(*Permission.objects.all())
            permission_assignment.save()

    def __str__(self):
        return self.name
