from django.contrib import admin
from .models import MFA, Channel, ChannelMembers, Permission, PermissionAssignment, SubChannel, Group, SubChannelGroupMembers, SubChannelMembers

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'name', 'description', 'logo_url')
    search_fields = ('name', 'description')
    list_filter = ('owner',)
    readonly_fields = ('logo_url',)

    def logo_url(self, obj):
        return obj.logo.url if obj.logo else None
    logo_url.short_description = 'Logo URL'

class SubChannelAdmin(admin.ModelAdmin):
    list_display = ('id','channel', 'name', 'description', 'logo_url')
    search_fields = ('name', 'description')
    list_filter = ('channel',)
    readonly_fields = ('logo_url',)

    def logo_url(self, obj):
        return obj.logo.url if obj.logo else None
    logo_url.short_description = 'Logo URL'

class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'subchannel', 'name', 'description', 'logo_url')
    search_fields = ('name', 'description')
    list_filter = ('subchannel',)
    readonly_fields = ('logo_url',)

    def logo_url(self, obj):
        return obj.logo.url if obj.logo else None
    logo_url.short_description = 'Logo URL'

class PermissionAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'permission_type', 'target_id', 'target_type', 'all_members')
    search_fields = ('permission_type', 'target_id', 'target_type')
    list_filter = ('permission', 'target_type', 'all_members')
    filter_horizontal = ('permission',)  # Removed 'members' from filter_horizontal

admin.site.register(Channel, ChannelAdmin)
admin.site.register(SubChannel, SubChannelAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Permission)
admin.site.register(PermissionAssignment, PermissionAssignmentAdmin)
admin.site.register(ChannelMembers)
admin.site.register(SubChannelMembers)
admin.site.register(SubChannelGroupMembers)
admin.site.register(MFA)
