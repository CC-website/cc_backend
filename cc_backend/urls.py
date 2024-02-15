from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Import drf-yasg
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="CC API",
        default_version='v1',
        description="CC"
    ),
    public=True,
)

urlpatterns = [
    path(r'', RedirectView.as_view(url='/admin/home', permanent=False), name='index'),
    path('admin/', admin.site.urls),
    path('api/', include('channels.urls')),
    path('user/', include('user.urls')),
    # ... include other app URLs ...

    # Swagger documentation URLs
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

# Add the following line to serve static files during development
# Remove it in production and configure your web server to serve static files.


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
