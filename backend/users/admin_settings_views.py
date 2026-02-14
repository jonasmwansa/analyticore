"""
Admin Alert Settings Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from .security_models import AdminAlertSettings, SecurityAuditLog


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_alert_settings(request):
    """Get current alert settings"""
    settings_obj = AdminAlertSettings.get_settings()
    
    return Response({
        'error_rate_threshold': settings_obj.error_rate_threshold,
        'db_response_threshold_ms': settings_obj.db_response_threshold_ms,
        'max_errors_24h': settings_obj.max_errors_24h,
        'alert_emails_enabled': settings_obj.alert_emails_enabled,
        'daily_summary_enabled': settings_obj.daily_summary_enabled,
        'additional_recipients': settings_obj.additional_recipients,
        'health_check_interval_minutes': settings_obj.health_check_interval_minutes,
        'updated_at': settings_obj.updated_at.isoformat() if settings_obj.updated_at else None,
        'updated_by': settings_obj.updated_by.email if settings_obj.updated_by else None
    })


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_alert_settings(request):
    """Update alert settings"""
    settings_obj = AdminAlertSettings.get_settings()
    
    # Update fields if provided
    if 'error_rate_threshold' in request.data:
        value = float(request.data['error_rate_threshold'])
        if value < 0 or value > 100:
            return Response(
                {'detail': 'Error rate threshold must be between 0 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        settings_obj.error_rate_threshold = value
    
    if 'db_response_threshold_ms' in request.data:
        value = int(request.data['db_response_threshold_ms'])
        if value < 10 or value > 10000:
            return Response(
                {'detail': 'DB response threshold must be between 10ms and 10000ms'},
                status=status.HTTP_400_BAD_REQUEST
            )
        settings_obj.db_response_threshold_ms = value
    
    if 'max_errors_24h' in request.data:
        value = int(request.data['max_errors_24h'])
        if value < 1 or value > 1000:
            return Response(
                {'detail': 'Max errors must be between 1 and 1000'},
                status=status.HTTP_400_BAD_REQUEST
            )
        settings_obj.max_errors_24h = value
    
    if 'alert_emails_enabled' in request.data:
        settings_obj.alert_emails_enabled = bool(request.data['alert_emails_enabled'])
    
    if 'daily_summary_enabled' in request.data:
        settings_obj.daily_summary_enabled = bool(request.data['daily_summary_enabled'])
    
    if 'additional_recipients' in request.data:
        # Validate email format
        recipients = request.data['additional_recipients']
        if recipients:
            import re
            emails = [e.strip() for e in recipients.split(',') if e.strip()]
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            for email in emails:
                if not re.match(email_pattern, email):
                    return Response(
                        {'detail': f'Invalid email format: {email}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        settings_obj.additional_recipients = recipients
    
    if 'health_check_interval_minutes' in request.data:
        value = int(request.data['health_check_interval_minutes'])
        if value < 5 or value > 60:
            return Response(
                {'detail': 'Health check interval must be between 5 and 60 minutes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        settings_obj.health_check_interval_minutes = value
    
    settings_obj.updated_by = request.user
    settings_obj.save()
    
    # Log the change
    SecurityAuditLog.log_event(
        'settings_changed',
        request.user,
        request.META.get('REMOTE_ADDR'),
        request.META.get('HTTP_USER_AGENT', '')[:500],
        {'settings_type': 'alert_settings'}
    )
    
    return Response({
        'message': 'Alert settings updated successfully',
        'error_rate_threshold': settings_obj.error_rate_threshold,
        'db_response_threshold_ms': settings_obj.db_response_threshold_ms,
        'max_errors_24h': settings_obj.max_errors_24h,
        'alert_emails_enabled': settings_obj.alert_emails_enabled,
        'daily_summary_enabled': settings_obj.daily_summary_enabled,
        'additional_recipients': settings_obj.additional_recipients,
        'health_check_interval_minutes': settings_obj.health_check_interval_minutes
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def test_alert_email(request):
    """Send a test alert email"""
    from django.core.mail import send_mail
    from django.conf import settings as django_settings
    from .models import User
    
    alert_settings = AdminAlertSettings.get_settings()
    
    # Get admin emails
    admin_emails = list(
        User.objects.filter(is_staff=True, is_active=True)
        .values_list('email', flat=True)
    )
    
    # Add additional recipients
    additional = alert_settings.get_recipient_list()
    all_recipients = list(set(admin_emails + additional))
    
    if not all_recipients:
        return Response(
            {'detail': 'No recipients configured'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        send_mail(
            subject='[AnalytiCore] Test Alert Email',
            message=f'''This is a test alert email from AnalytiCore.

Current Alert Settings:
- Error Rate Threshold: {alert_settings.error_rate_threshold}%
- DB Response Threshold: {alert_settings.db_response_threshold_ms}ms
- Max Errors (24h): {alert_settings.max_errors_24h}
- Health Check Interval: {alert_settings.health_check_interval_minutes} minutes

Recipients: {', '.join(all_recipients)}

If you received this email, your alert configuration is working correctly.

Best regards,
AnalytiCore System
''',
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=all_recipients,
            fail_silently=False
        )
        
        return Response({
            'message': 'Test email sent successfully',
            'recipients': all_recipients
        })
    except Exception as e:
        return Response(
            {'detail': f'Failed to send test email: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
