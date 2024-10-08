from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BroadcastViewSet

router = DefaultRouter()
router.register(r'broadcasts', BroadcastViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
