from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('<uuid:project_id>/analyze', views.analyze_data, name='analyze'),
    path('<uuid:project_id>/transform', views.apply_transformations, name='transform'),
]
