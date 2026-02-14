import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analyticore_api.settings')

app = Celery('analyticore')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'retry-failed-webhooks': {
        'task': 'users.tasks.retry_failed_webhooks_task',
        'schedule': crontab(minute='*/15'),
    },
    'cleanup-old-exports': {
        'task': 'exports.tasks.cleanup_old_exports',
        'schedule': crontab(hour=2, minute=0),
    },
    # System Health Monitoring
    'check-system-health': {
        'task': 'users.health_monitoring.check_system_health',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'daily-health-summary': {
        'task': 'users.health_monitoring.daily_health_summary',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')