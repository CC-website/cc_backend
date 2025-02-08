from django.urls import path, include
from .views import CheckContacts, LogoutAPIView, RegistrationAPIView, LoginAPIView, CheckLogin, UserInfoAPIView, GetUsers, PrivacySettingsAPIView, PrivacyExceptionsViewSet, messaging
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'privacy-exceptions', PrivacyExceptionsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('privacy-settings/', PrivacySettingsAPIView.as_view(), name='privacy-settings'),
    path('register/', RegistrationAPIView.as_view(), name='register-api'),
    path('login/', LoginAPIView.as_view(), name='login-api'),
    path('check_login_status/', CheckLogin.as_view(), name='check_login_status'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('user-info/', UserInfoAPIView.as_view(), name='user-info'),
    path('get-users/', GetUsers.as_view(), name='get_users'),
    path('messaging/', messaging),
    path('check-contacts/', CheckContacts.as_view(), name="check_contacts")
    # Add other user-related APIs as needed
]
