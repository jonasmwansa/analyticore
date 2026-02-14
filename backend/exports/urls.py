from django.urls import path
from . import views

app_name = 'exports'

urlpatterns = [
    path('<uuid:project_id>/export', views.export_data, name='export-data'),
    path('<uuid:project_id>/charts', views.generate_charts, name='generate-charts'),
]