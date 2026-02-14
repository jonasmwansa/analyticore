from django.urls import path
from . import admin_views, analytics_views, admin_settings_views

app_name = 'saas_admin'

urlpatterns = [
    # Legacy endpoints
    path('dashboard', admin_views.admin_dashboard_stats, name='dashboard'),
    path('users', admin_views.admin_users_list, name='users'),
    path('projects', admin_views.admin_projects_list, name='projects'),
    
    # Enhanced Analytics APIs
    path('analytics/summary', analytics_views.dashboard_summary, name='analytics_summary'),
    path('analytics/users', analytics_views.user_metrics, name='user_metrics'),
    path('analytics/user-growth', analytics_views.user_growth_chart, name='user_growth'),
    path('analytics/activity', analytics_views.activity_analytics, name='activity'),
    path('analytics/projects', analytics_views.project_analytics, name='project_analytics'),
    path('analytics/pipelines', analytics_views.pipeline_analytics, name='pipeline_analytics'),
    path('analytics/subscriptions', analytics_views.subscription_analytics, name='subscription_analytics'),
    path('analytics/retention', analytics_views.retention_analytics, name='retention'),
    path('analytics/funnel', analytics_views.funnel_analytics, name='funnel'),
    path('analytics/feed', analytics_views.recent_activity_feed, name='activity_feed'),
    path('analytics/health', analytics_views.system_health, name='system_health'),
    
    # Alert Settings
    path('settings/alerts', admin_settings_views.get_alert_settings, name='alert_settings_get'),
    path('settings/alerts/update', admin_settings_views.update_alert_settings, name='alert_settings_update'),
    path('settings/alerts/test-email', admin_settings_views.test_alert_email, name='alert_test_email'),
]