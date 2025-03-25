# urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from event.views import EventViewSet


# Router for default viewsets
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]