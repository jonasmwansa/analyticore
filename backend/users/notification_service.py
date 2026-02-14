from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for creating and sending notifications"""
    
    EMAIL_TEMPLATES = {
        'analysis_complete': {
            'subject': 'Your Analysis is Complete - AnalytiCore',
            'icon': '📊',
        },
        'data_issues': {
            'subject': 'Data Issues Found - AnalytiCore',
            'icon': '⚠️',
        },
        'export_ready': {
            'subject': 'Your Export is Ready - AnalytiCore',
            'icon': '📥',
        },
        'upload_complete': {
            'subject': 'Data Upload Complete - AnalytiCore',
            'icon': '✅',
        },
        'project_created': {
            'subject': 'New Project Created - AnalytiCore',
            'icon': '🆕',
        },
        'transformation_applied': {
            'subject': 'Transformation Applied - AnalytiCore',
            'icon': '🔄',
        },
        'system': {
            'subject': 'System Notification - AnalytiCore',
            'icon': 'ℹ️',
        },
    }
    
    @classmethod
    def create_notification(cls, user, notification_type, title, message, 
                           priority='medium', related_project_id=None,
                           related_object_type=None, related_object_id=None,
                           metadata=None, send_email=True, send_push=True):
        """Create a notification and optionally send email/push"""
        from .notification_models import Notification, NotificationPreference
        
        # Create the in-app notification
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            related_project_id=related_project_id,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
            metadata=metadata or {},
        )
        
        # Get user preferences
        prefs, _ = NotificationPreference.objects.get_or_create(user=user)
        
        # Send email notification if enabled
        if send_email and cls._should_send_email(prefs, notification_type):
            cls._send_email_notification(user, notification)
        
        # Send push notification if enabled
        if send_push and cls._should_send_push(prefs, notification_type):
            cls._send_push_notification(user, notification)
        
        return notification
    
    @classmethod
    def _should_send_email(cls, prefs, notification_type):
        """Check if email should be sent based on preferences"""
        if prefs.email_digest_frequency == 'never':
            return False
        
        email_prefs_map = {
            'analysis_complete': prefs.email_on_analysis_complete,
            'data_issues': prefs.email_on_data_issues,
            'export_ready': prefs.email_on_export_ready,
            'upload_complete': prefs.email_on_upload_complete,
        }
        
        return email_prefs_map.get(notification_type, True)
    
    @classmethod
    def _should_send_push(cls, prefs, notification_type):
        """Check if push should be sent based on preferences"""
        if not prefs.push_enabled:
            return False
        
        push_prefs_map = {
            'analysis_complete': prefs.push_on_analysis_complete,
            'data_issues': prefs.push_on_data_issues,
            'export_ready': prefs.push_on_export_ready,
        }
        
        return push_prefs_map.get(notification_type, True)
    
    @classmethod
    def _send_email_notification(cls, user, notification):
        """Send email notification"""
        template_info = cls.EMAIL_TEMPLATES.get(notification.notification_type, cls.EMAIL_TEMPLATES['system'])
        
        html_message = f"""
        <html>
          <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%); padding: 30px; text-align: center;">
              <h1 style="color: white; margin: 0; font-size: 24px;">AnalytiCore</h1>
            </div>
            <div style="padding: 30px; background: #ffffff;">
              <div style="font-size: 40px; text-align: center; margin-bottom: 20px;">{template_info['icon']}</div>
              <h2 style="color: #0F172A; margin: 0 0 15px 0; font-size: 22px;">{notification.title}</h2>
              <p style="color: #64748B; margin: 0 0 25px 0; font-size: 16px;">{notification.message}</p>
              
              <a href="{settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else 'http://localhost:3000'}/dashboard"
                 style="display: inline-block; padding: 14px 28px; background: #6366F1; 
                        color: white; text-decoration: none; border-radius: 8px; font-weight: 600;
                        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);">
                View in Dashboard
              </a>
            </div>
            <div style="padding: 20px; background: #F8FAFC; text-align: center; border-top: 1px solid #E2E8F0;">
              <p style="color: #94A3B8; font-size: 12px; margin: 0;">
                You're receiving this email because you enabled notifications for your AnalytiCore account.
                <br>
                <a href="{settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else 'http://localhost:3000'}/settings/notifications" 
                   style="color: #6366F1;">Manage notification preferences</a>
              </p>
            </div>
          </body>
        </html>
        """
        
        try:
            send_mail(
                template_info['subject'],
                notification.message,  # Plain text fallback
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            notification.email_sent = True
            notification.email_sent_at = timezone.now()
            notification.save(update_fields=['email_sent', 'email_sent_at'])
            
            logger.info(f"Email notification sent to {user.email}: {notification.title}")
        except Exception as e:
            logger.error(f"Failed to send email notification to {user.email}: {e}")
    
    @classmethod
    def _send_push_notification(cls, user, notification):
        """Send push notification to all user's subscribed devices"""
        from .notification_models import PushSubscription
        
        subscriptions = PushSubscription.objects.filter(user=user, is_active=True)
        
        if not subscriptions.exists():
            return
        
        template_info = cls.EMAIL_TEMPLATES.get(notification.notification_type, cls.EMAIL_TEMPLATES['system'])
        
        payload = {
            'title': notification.title,
            'body': notification.message,
            'icon': '/logo192.png',
            'badge': '/badge.png',
            'tag': str(notification.notification_id),
            'data': {
                'notification_id': str(notification.notification_id),
                'type': notification.notification_type,
                'project_id': str(notification.related_project_id) if notification.related_project_id else None,
                'url': '/dashboard',
            }
        }
        
        # Try to send to each subscription
        for subscription in subscriptions:
            try:
                cls._send_web_push(subscription, payload)
                logger.info(f"Push notification sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send push notification: {e}")
                # Mark subscription as inactive if it failed
                if 'expired' in str(e).lower() or 'unsubscribed' in str(e).lower():
                    subscription.is_active = False
                    subscription.save(update_fields=['is_active'])
        
        notification.push_sent = True
        notification.push_sent_at = timezone.now()
        notification.save(update_fields=['push_sent', 'push_sent_at'])
    
    @classmethod
    def _send_web_push(cls, subscription, payload):
        """Send a web push notification"""
        try:
            from pywebpush import webpush, WebPushException
        except ImportError:
            logger.warning("pywebpush not installed, skipping push notification")
            return
        
        vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
        vapid_claims = {
            'sub': f"mailto:{settings.DEFAULT_FROM_EMAIL}"
        }
        
        if not vapid_private_key:
            logger.warning("VAPID_PRIVATE_KEY not configured, skipping push notification")
            return
        
        try:
            webpush(
                subscription_info={
                    'endpoint': subscription.endpoint,
                    'keys': {
                        'p256dh': subscription.p256dh_key,
                        'auth': subscription.auth_key,
                    }
                },
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims,
            )
        except WebPushException as e:
            logger.error(f"Web push failed: {e}")
            raise
    
    @classmethod
    def mark_as_read(cls, notification_id, user):
        """Mark a notification as read"""
        from .notification_models import Notification
        
        notification = Notification.objects.filter(
            notification_id=notification_id,
            user=user
        ).first()
        
        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=['is_read', 'read_at'])
        
        return notification
    
    @classmethod
    def mark_all_as_read(cls, user):
        """Mark all notifications as read for a user"""
        from .notification_models import Notification
        
        return Notification.objects.filter(
            user=user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
    
    @classmethod
    def get_unread_count(cls, user):
        """Get count of unread notifications"""
        from .notification_models import Notification
        
        return Notification.objects.filter(user=user, is_read=False).count()
