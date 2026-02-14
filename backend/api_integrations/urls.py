from django.urls import path
from . import views

app_name = 'api_integrations'

urlpatterns = [
    path('mysql/test', views.test_mysql_connection, name='test-mysql'),
    path('sources', views.list_data_sources, name='list-sources'),
    path('sources/create', views.create_data_source, name='create-source'),
    path('sources/<uuid:source_id>/import', views.import_from_mysql, name='import-mysql'),
]
