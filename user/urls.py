from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.profile_views import UserProfileViewSet
from .views import LogoutAPIView, RegistrationAPIView, LoginAPIView, CheckLogin, UserInfoAPIView, GetUsers

router = DefaultRouter()
router.register(r'user-info', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('', include(router.urls)),  # Ensure you include the router urls for viewset registration
    path('register/', RegistrationAPIView.as_view(), name='register-api'),
    path('login/', LoginAPIView.as_view(), name='login-api'),
    path('check_login_status/', CheckLogin.as_view(), name='check_login_status'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('get-users/', GetUsers.as_view(), name='get_users'),
    # Add other user-related APIs as needed
]
