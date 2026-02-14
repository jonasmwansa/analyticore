from django.urls import path
from . import billing_views

app_name = 'billing'

urlpatterns = [
    path('plans', billing_views.get_billing_plans, name='plans'),
    path('checkout', billing_views.create_checkout_session, name='checkout'),
    path('webhook', billing_views.stripe_webhook, name='stripe-webhook'),
    path('history', billing_views.get_payment_history, name='payment-history'),
]
