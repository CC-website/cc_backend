# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'about', 'phone_number','code', 'password','is_active', 'is_staff', 'last_login', 'publicKey')

# Register the custom admin class
admin.site.register(User, CustomUserAdmin)
