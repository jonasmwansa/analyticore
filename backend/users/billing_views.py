import stripe
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .billing_models import StripeCustomer, BillingPlan, PaymentHistory
from .saas_models import Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else None

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_billing_plans(request):
    plans = BillingPlan.objects.filter(is_active=True)
    return Response({
        'plans': [{
            'plan_id': str(p.plan_id),
            'name': p.name,
            'plan_type': p.plan_type,
            'price_monthly': str(p.price_monthly),
            'price_yearly': str(p.price_yearly),
            'max_projects': p.max_projects,
            'max_rows_per_project': p.max_rows_per_project,
            'max_ai_analyses_per_month': p.max_ai_analyses_per_month,
            'features': p.features
        } for p in plans]
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    plan_id = request.data.get('plan_id')
    billing_period = request.data.get('billing_period', 'monthly')
    
    try:
        plan = BillingPlan.objects.get(plan_id=plan_id)
    except BillingPlan.DoesNotExist:
        return Response({'detail': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not stripe.api_key:
        return Response({'detail': 'Stripe not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    try:
        customer, created = StripeCustomer.objects.get_or_create(
            user=request.user,
            defaults={'stripe_customer_id': ''}
        )
        
        if not customer.stripe_customer_id:
            stripe_customer = stripe.Customer.create(
                email=request.user.email,
                metadata={'user_id': str(request.user.user_id)}
            )
            customer.stripe_customer_id = stripe_customer.id
            customer.save()
        
        price_amount = int(float(plan.price_yearly if billing_period == 'yearly' else plan.price_monthly) * 100)
        
        session = stripe.checkout.Session.create(
            customer=customer.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': plan.name,
                        'description': f'{plan.plan_type.capitalize()} Plan - {billing_period.capitalize()}'
                    },
                    'unit_amount': price_amount,
                    'recurring': {
                        'interval': 'year' if billing_period == 'yearly' else 'month'
                    }
                },
                'quantity': 1
            }],
            mode='subscription',
            success_url=request.build_absolute_uri('/dashboard?payment=success'),
            cancel_url=request.build_absolute_uri('/dashboard?payment=cancelled'),
            metadata={
                'user_id': str(request.user.user_id),
                'plan_id': str(plan.plan_id)
            }
        )
        
        return Response({'checkout_url': session.url})
    
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    if not stripe.api_key:
        return Response({'detail': 'Stripe not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return Response({'detail': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        return Response({'detail': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        plan_id = session['metadata']['plan_id']
        
        from users.models import User
        user = User.objects.get(user_id=user_id)
        plan = BillingPlan.objects.get(plan_id=plan_id)
        
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            defaults={'plan': plan.plan_type, 'status': 'active'}
        )
        if not created:
            subscription.plan = plan.plan_type
            subscription.status = 'active'
            subscription.save()
        
        PaymentHistory.objects.create(
            user=user,
            stripe_payment_intent_id=session['payment_intent'],
            amount=session['amount_total'] / 100,
            status='succeeded',
            plan=plan,
            billing_period='monthly'
        )
    
    return Response({'status': 'success'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_history(request):
    payments = PaymentHistory.objects.filter(user=request.user)[:50]
    return Response({
        'payments': [{
            'payment_id': str(p.payment_id),
            'amount': str(p.amount),
            'currency': p.currency,
            'status': p.status,
            'plan': p.plan.name if p.plan else None,
            'created_at': p.created_at
        } for p in payments]
    })