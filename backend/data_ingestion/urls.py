from django.urls import path
from . import views

app_name = 'data_ingestion'

urlpatterns = [
    path('<uuid:project_id>/upload', views.upload_file, name='upload'),
    path('<uuid:project_id>/data', views.get_data_preview, name='data-preview'),
]
