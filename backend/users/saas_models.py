from django.db import models
from django.conf import settings
import uuid

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free Plan'),
        ('starter', 'Starter Plan'),
        ('professional', 'Professional Plan'),
        ('enterprise', 'Enterprise Plan'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('trial', 'Trial'),
    ]
    
    subscription_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'subscriptions'

class UsageTracking(models.Model):
    tracking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='usage')
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=50)
    resource_id = models.UUIDField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'usage_tracking'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]