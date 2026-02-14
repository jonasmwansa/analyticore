from django.urls import path
from . import notification_views

app_name = 'notifications'

urlpatterns = [
    # Notifications
    path('', notification_views.list_notifications, name='list'),
    path('summary', notification_views.get_notification_summary, name='summary'),
    path('<uuid:notification_id>/read', notification_views.mark_notification_read, name='mark-read'),
    path('read-all', notification_views.mark_all_read, name='mark-all-read'),
    path('<uuid:notification_id>', notification_views.delete_notification, name='delete'),
    
    # Preferences
    path('preferences', notification_views.notification_preferences, name='preferences'),
    
    # Push notifications
    path('push/subscribe', notification_views.subscribe_push, name='push-subscribe'),
    path('push/unsubscribe', notification_views.unsubscribe_push, name='push-unsubscribe'),
    path('push/vapid-key', notification_views.get_vapid_public_key, name='vapid-key'),
    
    # Test
    path('test', notification_views.test_notification, name='test'),
]
