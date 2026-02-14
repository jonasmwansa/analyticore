from django.db import models
from django.conf import settings
import uuid

class NotificationPreference(models.Model):
    """User preferences for notifications"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notification_preferences'
    )
    
    # Email notifications
    email_on_analysis_complete = models.BooleanField(default=True)
    email_on_data_issues = models.BooleanField(default=True)
    email_on_export_ready = models.BooleanField(default=True)
    email_on_upload_complete = models.BooleanField(default=True)
    email_on_pipeline_complete = models.BooleanField(default=True)
    email_on_pipeline_failed = models.BooleanField(default=True)
    email_digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('instant', 'Instant'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest'),
            ('never', 'Never'),
        ],
        default='instant'
    )
    
    # Push notifications
    push_enabled = models.BooleanField(default=False)
    push_on_analysis_complete = models.BooleanField(default=True)
    push_on_data_issues = models.BooleanField(default=True)
    push_on_export_ready = models.BooleanField(default=True)
    push_on_pipeline_complete = models.BooleanField(default=True)
    push_on_pipeline_failed = models.BooleanField(default=True)
    
    # In-app notifications
    inapp_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"Notification Preferences for {self.user.email}"


class Notification(models.Model):
    """In-app notifications"""
    NOTIFICATION_TYPES = [
        ('analysis_complete', 'Analysis Complete'),
        ('data_issues', 'Data Issues Found'),
        ('export_ready', 'Export Ready'),
        ('upload_complete', 'Upload Complete'),
        ('project_created', 'Project Created'),
        ('transformation_applied', 'Transformation Applied'),
        ('pipeline_complete', 'Pipeline Complete'),
        ('pipeline_failed', 'Pipeline Failed'),
        ('system', 'System Notification'),
        ('system_alert', 'System Alert'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    notification_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    # Related object (optional)
    related_project_id = models.UUIDField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True, default='')
    related_object_id = models.UUIDField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Email tracking
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Push tracking
    push_sent = models.BooleanField(default=False)
    push_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"


class PushSubscription(models.Model):
    """Browser push notification subscriptions"""
    subscription_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='push_subscriptions'
    )
    
    endpoint = models.TextField(unique=True)
    p256dh_key = models.CharField(max_length=255)
    auth_key = models.CharField(max_length=255)
    
    user_agent = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'push_subscriptions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"Push subscription for {self.user.email}"
