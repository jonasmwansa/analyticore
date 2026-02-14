from django.db import models
from django.conf import settings
import uuid

class Webhook(models.Model):
    EVENT_TYPES = [
        ('project.created', 'Project Created'),
        ('project.uploaded', 'Data Uploaded'),
        ('project.analyzed', 'Analysis Complete'),
        ('project.transformed', 'Transformation Complete'),
        ('project.exported', 'Export Complete'),
        ('project.failed', 'Processing Failed'),
    ]
    
    webhook_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='webhooks')
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=500)
    event_types = models.JSONField(default=list, help_text="List of event types to trigger this webhook")
    secret = models.CharField(max_length=255, help_text="Secret for webhook signature verification")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'webhooks'
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.url}"

class WebhookDelivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    delivery_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_status = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'webhook_deliveries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.status}"
