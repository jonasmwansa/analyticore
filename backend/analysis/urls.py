from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('<uuid:project_id>/analyze', views.analyze_data, name='analyze'),
    path('<uuid:project_id>/transform', views.apply_transformations, name='transform'),
    path('<uuid:project_id>/statistics', views.get_statistics, name='statistics'),
    path('<uuid:project_id>/correlation', views.get_correlation, name='correlation'),
    path('<uuid:project_id>/distribution', views.get_distribution, name='distribution'),
    path('<uuid:project_id>/chart', views.get_chart_data, name='chart'),
    path('<uuid:project_id>/column', views.get_column_info, name='column-info'),
    path('<uuid:project_id>/columns', views.get_columns, name='columns'),
]
