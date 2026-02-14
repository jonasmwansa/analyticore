from django.urls import path
from . import admin_views

app_name = 'saas_admin'

urlpatterns = [
    path('dashboard', admin_views.admin_dashboard_stats, name='dashboard'),
    path('users', admin_views.admin_users_list, name='users'),
    path('projects', admin_views.admin_projects_list, name='projects'),
]