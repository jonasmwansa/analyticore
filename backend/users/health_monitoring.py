"""
System Health Monitoring Tasks
Monitors system health metrics and sends alerts when thresholds are exceeded
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.db import connection
from datetime import timedelta
import logging
import time

logger = logging.getLogger(__name__)

# Alert thresholds
THRESHOLDS = {
    'error_rate': 5.0,  # Alert if error rate > 5%
    'db_response_ms': 500,  # Alert if DB response > 500ms
    'errors_24h': 10,  # Alert if more than 10 errors in 24h
}


@shared_task
def check_system_health():
    """
    Periodic task to check system health and send alerts if needed.
    Runs every 15 minutes via Celery Beat.
    """
    from users.models import User
    from pipelines.models import PipelineRun
    
    logger.info("Running system health check...")
    
    alerts = []
    now = timezone.now()
    
    # Check database response time
    start = time.time()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_response_ms = round((time.time() - start) * 1000, 2)
        
        if db_response_ms > THRESHOLDS['db_response_ms']:
            alerts.append({
                'type': 'db_slow',
                'severity': 'warning' if db_response_ms < 1000 else 'critical',
                'message': f'Database response time is {db_response_ms}ms (threshold: {THRESHOLDS["db_response_ms"]}ms)'
            })
    except Exception as e:
        alerts.append({
            'type': 'db_error',
            'severity': 'critical',
            'message': f'Database connection error: {str(e)}'
        })
        db_response_ms = None
    
    # Check error rate from pipeline runs
    try:
        total_runs_24h = PipelineRun.objects.filter(
            started_at__gte=now - timedelta(hours=24)
        ).count()
        
        failed_runs_24h = PipelineRun.objects.filter(
            started_at__gte=now - timedelta(hours=24),
            status='failed'
        ).count()
        
        if total_runs_24h > 0:
            error_rate = round((failed_runs_24h / total_runs_24h) * 100, 2)
            
            if error_rate > THRESHOLDS['error_rate']:
                alerts.append({
                    'type': 'high_error_rate',
                    'severity': 'critical' if error_rate > 20 else 'warning',
                    'message': f'Error rate is {error_rate}% ({failed_runs_24h}/{total_runs_24h} failed runs in 24h)'
                })
        
        if failed_runs_24h > THRESHOLDS['errors_24h']:
            alerts.append({
                'type': 'error_spike',
                'severity': 'critical',
                'message': f'{failed_runs_24h} failed pipeline runs in the last 24 hours (threshold: {THRESHOLDS["errors_24h"]})'
            })
    except Exception as e:
        logger.error(f"Error checking pipeline runs: {str(e)}")
    
    # Send alerts if any found
    if alerts:
        send_health_alerts.delay(alerts)
        
        # Also create in-app notifications for admin users
        create_admin_notifications(alerts)
    
    logger.info(f"System health check complete. Alerts: {len(alerts)}")
    
    return {
        'status': 'healthy' if not alerts else 'alert',
        'alerts_count': len(alerts),
        'db_response_ms': db_response_ms,
        'checked_at': now.isoformat()
    }


@shared_task
def send_health_alerts(alerts):
    """
    Send email alerts to admin users
    """
    from users.models import User
    
    # Get all admin users
    admin_emails = list(
        User.objects.filter(is_staff=True, is_active=True)
        .values_list('email', flat=True)
    )
    
    if not admin_emails:
        logger.warning("No admin users found to send health alerts to")
        return
    
    # Build alert email
    critical_alerts = [a for a in alerts if a['severity'] == 'critical']
    warning_alerts = [a for a in alerts if a['severity'] == 'warning']
    
    subject = f"[AnalytiCore] System Health Alert - {len(critical_alerts)} Critical, {len(warning_alerts)} Warnings"
    
    message_lines = [
        "AnalytiCore System Health Alert",
        "=" * 40,
        f"Checked at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
    ]
    
    if critical_alerts:
        message_lines.append("🔴 CRITICAL ALERTS:")
        message_lines.append("-" * 20)
        for alert in critical_alerts:
            message_lines.append(f"  • [{alert['type']}] {alert['message']}")
        message_lines.append("")
    
    if warning_alerts:
        message_lines.append("⚠️ WARNINGS:")
        message_lines.append("-" * 20)
        for alert in warning_alerts:
            message_lines.append(f"  • [{alert['type']}] {alert['message']}")
        message_lines.append("")
    
    message_lines.extend([
        "",
        "Please review the admin dashboard for more details:",
        f"{getattr(settings, 'APP_URL', 'https://analyticore.com')}/admin",
        "",
        "---",
        "This is an automated alert from AnalytiCore System Monitoring."
    ])
    
    message = "\n".join(message_lines)
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            fail_silently=False
        )
        logger.info(f"Health alert email sent to {len(admin_emails)} admins")
    except Exception as e:
        logger.error(f"Failed to send health alert email: {str(e)}")


def create_admin_notifications(alerts):
    """
    Create in-app notifications for admin users
    """
    try:
        from users.notification_service import NotificationService
        from users.models import User
        
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        
        critical_count = len([a for a in alerts if a['severity'] == 'critical'])
        
        if critical_count > 0:
            title = f"🔴 System Critical Alert: {critical_count} issues detected"
            priority = 'high'
        else:
            title = f"⚠️ System Warning: {len(alerts)} issues detected"
            priority = 'medium'
        
        message = "\n".join([f"• {a['message']}" for a in alerts])
        
        for admin in admin_users:
            NotificationService.create_notification(
                user=admin,
                notification_type='system_alert',
                title=title,
                message=message,
                priority=priority,
                metadata={
                    'alerts': alerts,
                    'checked_at': timezone.now().isoformat()
                },
                send_email=False,  # Already sent via send_health_alerts
                send_push=True
            )
        
        logger.info(f"Created in-app notifications for {admin_users.count()} admins")
    except Exception as e:
        logger.error(f"Failed to create admin notifications: {str(e)}")


@shared_task
def daily_health_summary():
    """
    Send daily health summary email to admins
    Runs once per day at 8:00 AM
    """
    from users.models import User
    from projects.models import Project
    from pipelines.models import PipelineRun
    
    now = timezone.now()
    yesterday = now - timedelta(days=1)
    
    # Gather stats
    total_users = User.objects.count()
    new_users_24h = User.objects.filter(date_joined__gte=yesterday).count()
    active_users_24h = User.objects.filter(last_login__gte=yesterday).count()
    
    total_projects = Project.objects.count()
    new_projects_24h = Project.objects.filter(created_at__gte=yesterday).count()
    
    total_runs_24h = PipelineRun.objects.filter(started_at__gte=yesterday).count()
    successful_runs = PipelineRun.objects.filter(
        started_at__gte=yesterday, status='completed'
    ).count()
    failed_runs = PipelineRun.objects.filter(
        started_at__gte=yesterday, status='failed'
    ).count()
    
    success_rate = round((successful_runs / max(total_runs_24h, 1)) * 100, 1)
    
    # Build email
    admin_emails = list(
        User.objects.filter(is_staff=True, is_active=True)
        .values_list('email', flat=True)
    )
    
    if not admin_emails:
        return
    
    subject = f"[AnalytiCore] Daily Health Summary - {now.strftime('%Y-%m-%d')}"
    
    message = f"""
AnalytiCore Daily Health Summary
================================
Date: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}

📊 USER METRICS
--------------
Total Users: {total_users}
New Users (24h): {new_users_24h}
Active Users (24h): {active_users_24h}

📁 PROJECT METRICS
-----------------
Total Projects: {total_projects}
New Projects (24h): {new_projects_24h}

⚡ PIPELINE METRICS (24h)
------------------------
Total Runs: {total_runs_24h}
Successful: {successful_runs}
Failed: {failed_runs}
Success Rate: {success_rate}%

---
View full analytics: {getattr(settings, 'APP_URL', 'https://analyticore.com')}/admin

This is an automated summary from AnalytiCore.
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            fail_silently=False
        )
        logger.info("Daily health summary sent to admins")
    except Exception as e:
        logger.error(f"Failed to send daily summary: {str(e)}")
