import requests
import hashlib
import hmac
import json
from django.utils import timezone
from .webhook_models import WebhookDelivery
import logging

logger = logging.getLogger(__name__)

def trigger_webhook(user, event_type, payload):
    """Trigger all active webhooks for a user and event type"""
    from .webhook_models import Webhook
    
    webhooks = Webhook.objects.filter(
        user=user,
        is_active=True
    )
    
    for webhook in webhooks:
        if event_type in webhook.event_types or '*' in webhook.event_types:
            send_webhook(webhook, event_type, payload)

def send_webhook(webhook, event_type, payload):
    """Send webhook with signature and retry logic"""
    delivery = WebhookDelivery.objects.create(
        webhook=webhook,
        event_type=event_type,
        payload=payload,
        status='pending'
    )
    
    try:
        # Create signature
        payload_json = json.dumps(payload)
        signature = hmac.new(
            webhook.secret.encode('utf-8'),
            payload_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'Content-Type': 'application/json',
            'X-AnalytiCore-Event': event_type,
            'X-AnalytiCore-Signature': f'sha256={signature}',
            'X-AnalytiCore-Delivery': str(delivery.delivery_id),
        }
        
        response = requests.post(
            webhook.url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        delivery.response_status = response.status_code
        delivery.response_body = response.text[:1000]
        delivery.delivered_at = timezone.now()
        
        if 200 <= response.status_code < 300:
            delivery.status = 'success'
        else:
            delivery.status = 'failed'
            logger.warning(f"Webhook delivery failed: {response.status_code}")
        
        delivery.save()
        
    except Exception as e:
        delivery.status = 'failed'
        delivery.response_body = str(e)[:1000]
        delivery.save()
        logger.error(f"Webhook delivery error: {str(e)}")

def retry_failed_webhooks():
    """Retry failed webhook deliveries (run via Celery)"""
    failed = WebhookDelivery.objects.filter(
        status='failed',
        retry_count__lt=3
    ).select_related('webhook')
    
    for delivery in failed:
        delivery.retry_count += 1
        delivery.status = 'retrying'
        delivery.save()
        
        send_webhook(
            delivery.webhook,
            delivery.event_type,
            delivery.payload
        )
