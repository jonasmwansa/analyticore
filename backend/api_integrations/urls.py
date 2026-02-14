from django.urls import path
from . import views

app_name = 'api_integrations'

urlpatterns = [
    # MySQL
    path('mysql/test', views.test_mysql_connection, name='test-mysql'),
    
    # PostgreSQL
    path('postgresql/test', views.test_postgresql_connection, name='test-postgresql'),
    
    # Data Sources CRUD
    path('sources', views.list_data_sources, name='list-sources'),
    path('sources/create', views.create_data_source, name='create-source'),
    path('sources/<uuid:source_id>', views.delete_data_source, name='delete-source'),
    path('sources/<uuid:source_id>/import/mysql', views.import_from_mysql, name='import-mysql'),
    path('sources/<uuid:source_id>/import/postgresql', views.import_from_postgresql, name='import-postgresql'),
    
    # Google Sheets OAuth
    path('google-sheets/status', views.google_sheets_status, name='sheets-status'),
    path('google-sheets/auth', views.google_sheets_auth_url, name='sheets-auth'),
    path('google-sheets/callback', views.google_sheets_callback, name='sheets-callback'),
    path('google-sheets/disconnect', views.google_sheets_disconnect, name='sheets-disconnect'),
    
    # Google Sheets Data
    path('google-sheets/list', views.google_sheets_list, name='sheets-list'),
    path('google-sheets/<str:spreadsheet_id>/metadata', views.google_sheets_metadata, name='sheets-metadata'),
    path('google-sheets/<str:spreadsheet_id>/preview', views.google_sheets_preview, name='sheets-preview'),
    path('google-sheets/<uuid:project_id>/import', views.google_sheets_import, name='sheets-import'),
    
    # Direct Database Import to Project
    path('database/<uuid:project_id>/import', views.import_database_to_project, name='database-import'),
]
