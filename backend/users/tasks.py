from celery import shared_task
from users.webhook_utils import retry_failed_webhooks, trigger_webhook
from users.saas_models import UsageTracking
import logging

logger = logging.getLogger(__name__)

@shared_task
def retry_failed_webhooks_task():
    """Retry failed webhook deliveries"""
    retry_failed_webhooks()
    logger.info("Retried failed webhooks")

@shared_task
def send_webhook_task(user_id, event_type, payload):
    """Send webhook asynchronously"""
    from users.models import User
    try:
        user = User.objects.get(user_id=user_id)
        trigger_webhook(user, event_type, payload)
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for webhook")

@shared_task
def track_usage(user_id, action, resource_type, resource_id=None, metadata=None):
    """Track user usage asynchronously"""
    try:
        UsageTracking.objects.create(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {}
        )
    except Exception as e:
        logger.error(f"Usage tracking failed: {str(e)}")

@shared_task
def send_notification_task(user_id, notification_type, title, message, **kwargs):
    """Send notification asynchronously"""
    from users.models import User
    from users.notification_service import NotificationService
    try:
        user = User.objects.get(id=user_id)
        NotificationService.create_notification(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            **kwargs
        )
        logger.info(f"Notification sent to user {user_id}: {title}")
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for notification")
    except Exception as e:
        logger.error(f"Notification sending failed: {str(e)}")

@shared_task
def send_email_notification_task(user_id, subject, message, html_message=None):
    """Send email notification asynchronously"""
    from users.models import User
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        user = User.objects.get(id=user_id)
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent to {user.email}: {subject}")
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for email")
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")