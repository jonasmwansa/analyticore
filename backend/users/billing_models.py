from django.db import models
from django.conf import settings
import uuid

class StripeCustomer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stripe_customer')
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stripe_customers'

class BillingPlan(models.Model):
    PLAN_TYPES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    plan_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    stripe_price_id = models.CharField(max_length=255, blank=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    
    max_projects = models.IntegerField(default=5)
    max_rows_per_project = models.IntegerField(default=10000)
    max_ai_analyses_per_month = models.IntegerField(default=10)
    features = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'billing_plans'
    
    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/mo"

class PaymentHistory(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    payment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    plan = models.ForeignKey(BillingPlan, on_delete=models.SET_NULL, null=True)
    billing_period = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_history'
        ordering = ['-created_at']