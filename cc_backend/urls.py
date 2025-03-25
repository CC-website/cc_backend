from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView

# Import drf-yasg
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.conf.urls.static import static

from user.routing import websocket_urlpatterns

schema_view = get_schema_view(
    openapi.Info(
        title="CC API",
        default_version='v1',
        description="CC"
    ),
    public=True,
)

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/home', permanent=False), name='index'),
    path('admin/', admin.site.urls),
    path('api/', include('community.urls')),
    path('api/', include('messaging.urls')),
    path('api/', include('event.urls')),
    path('api/', include('broadcast.urls')),
    path('user/', include('user.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # Include WebSocket URL routing
    re_path(r'ws/', include((websocket_urlpatterns, 'websocket'))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
