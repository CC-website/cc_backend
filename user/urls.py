from django.urls import path
from .views import LogoutAPIView, RegistrationAPIView, LoginAPIView, CheckLogin, UserInfoAPIView

urlpatterns = [
    path('register/', RegistrationAPIView.as_view(), name='register-api'),
    path('login/', LoginAPIView.as_view(), name='login-api'),
    path('check_login_status/', CheckLogin.as_view(), name='check_login_status'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('user-info/', UserInfoAPIView.as_view(), name='user-info'),
    # Add other user-related APIs as needed
]
