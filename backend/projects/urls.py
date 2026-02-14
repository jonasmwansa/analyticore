from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import compare_views

app_name = 'projects'

router = DefaultRouter()
router.register(r'', views.ProjectViewSet, basename='project')

urlpatterns = [
    # Compare Projects Endpoints
    path('compare/', compare_views.compare_projects, name='compare-projects'),
    path('comparable/', compare_views.get_comparable_projects, name='comparable-projects'),
    
    path('', include(router.urls)),
]