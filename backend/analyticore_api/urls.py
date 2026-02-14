from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="AnalytiCore API",
      default_version='v1',
      description="Automated Data Analysis Pipeline API",
      contact=openapi.Contact(email="support@analyticore.com"),
      license=openapi.License(name="Proprietary"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    path('api/auth/', include('users.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/projects/', include('data_ingestion.urls')),
    path('api/analysis/', include('analysis.urls')),
    path('api/exports/', include('exports.urls')),
    path('api/integrations/', include('api_integrations.urls')),
    path('api/saas-admin/', include('users.admin_urls')),
    path('api/billing/', include('users.billing_urls')),
]
