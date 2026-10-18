"""
URL configuration for the Scrap Marketplace API.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Scrap Marketplace API",
        default_version='v1',
        description="REST API for the Scrap Recycling Marketplace platform.",
        contact=openapi.Contact(email="saumyashukla788708@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Swagger / ReDoc docs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # API v1
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/customers/', include('apps.customers.urls')),
    path('api/v1/catalog/', include('apps.catalog.urls')),
    path('api/v1/pickups/', include('apps.pickups.urls')),
    path('api/v1/collectors/', include('apps.accounts.collector_urls')),
    path('api/v1/wallet/', include('apps.wallet.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
