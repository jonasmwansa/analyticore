"""
Comprehensive Analytics API for Admin Dashboard
Implements user metrics, activity analytics, system performance, and business analytics
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDate, TruncHour, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict

from users.models import User
from users.saas_models import Subscription, UsageTracking
from projects.models import Project
from analysis.models import AnalysisRun, TransformationLog
from pipelines.models import ScheduledPipeline, PipelineRun


@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_metrics(request):
    """
    Key user metrics: DAU, WAU, MAU, stickiness, growth, churn
    """
    now = timezone.now()
    today = now.date()
    
    # Basic counts
    total_users = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    
    # Active users based on last_login
    active_today = User.objects.filter(last_login__date=today).count()
    active_week = User.objects.filter(last_login__gte=now - timedelta(days=7)).count()
    active_month = User.objects.filter(last_login__gte=now - timedelta(days=30)).count()
    
    # Stickiness = DAU / MAU
    stickiness = round((active_today / active_month * 100), 1) if active_month > 0 else 0
    
    # Growth rate (week over week)
    this_week_new = User.objects.filter(date_joined__gte=now - timedelta(days=7)).count()
    last_week_new = User.objects.filter(
        date_joined__gte=now - timedelta(days=14),
        date_joined__lt=now - timedelta(days=7)
    ).count()
    growth_rate = round(((this_week_new - last_week_new) / max(last_week_new, 1)) * 100, 1)
    
    # Churned users (not seen in 30+ days)
    churned = User.objects.filter(
        last_login__lt=now - timedelta(days=30)
    ).exclude(last_login__isnull=True).count()
    
    # Returning users (active today who were also active before today)
    returning = User.objects.filter(
        last_login__date=today,
        date_joined__lt=today
    ).count()
    
    # Verification rate
    verified = User.objects.filter(is_verified=True).count()
    verification_rate = round((verified / total_users * 100), 1) if total_users > 0 else 0
    
    return Response({
        'total_users': total_users,
        'new_users_today': new_users_today,
        'dau': active_today,
        'wau': active_week,
        'mau': active_month,
        'stickiness': stickiness,
        'growth_rate': growth_rate,
        'churned_users': churned,
        'returning_users': returning,
        'verified_users': verified,
        'verification_rate': verification_rate
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_growth_chart(request):
    """
    User growth over time for charting
    """
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Daily new users
    daily_signups = User.objects.filter(
        date_joined__gte=start_date
    ).annotate(
        date=TruncDate('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Cumulative users
    result = []
    cumulative = User.objects.filter(date_joined__lt=start_date).count()
    
    date_data = {item['date']: item['count'] for item in daily_signups}
    current = start_date.date()
    end = timezone.now().date()
    
    while current <= end:
        new_count = date_data.get(current, 0)
        cumulative += new_count
        result.append({
            'date': current.isoformat(),
            'new_users': new_count,
            'total_users': cumulative
        })
        current += timedelta(days=1)
    
    return Response({'data': result})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def activity_analytics(request):
    """
    Activity analytics: feature usage, sessions, actions
    """
    now = timezone.now()
    days = int(request.query_params.get('days', 30))
    start_date = now - timedelta(days=days)
    
    # Get all usage tracking for period
    usage = UsageTracking.objects.filter(timestamp__gte=start_date)
    
    # Action breakdown
    action_counts = usage.values('action').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Resource type breakdown
    resource_counts = usage.values('resource_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Daily activity
    daily_activity = usage.annotate(
        date=TruncDate('timestamp')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Hour of day distribution
    hour_distribution = {}
    for item in usage:
        hour = item.timestamp.hour
        hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
    
    # Power users (top 10 most active)
    power_users = usage.values('user__email', 'user__name').annotate(
        action_count=Count('id')
    ).order_by('-action_count')[:10]
    
    return Response({
        'top_actions': list(action_counts),
        'resource_types': list(resource_counts),
        'daily_activity': list(daily_activity),
        'hour_distribution': [{'hour': h, 'count': c} for h, c in sorted(hour_distribution.items())],
        'power_users': list(power_users)
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def project_analytics(request):
    """
    Project and analysis analytics
    """
    now = timezone.now()
    days = int(request.query_params.get('days', 30))
    start_date = now - timedelta(days=days)
    
    # Total projects
    total_projects = Project.objects.count()
    projects_this_period = Project.objects.filter(created_at__gte=start_date).count()
    
    # Projects by status
    status_breakdown = Project.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Projects by source type
    source_breakdown = Project.objects.values('source_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Daily project creation
    daily_projects = Project.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Data volume stats
    total_rows = Project.objects.aggregate(total=Sum('row_count'))['total'] or 0
    avg_rows = Project.objects.filter(row_count__isnull=False).aggregate(
        avg=Avg('row_count')
    )['avg'] or 0
    
    # Analysis runs
    total_analyses = AnalysisRun.objects.count()
    analyses_this_period = AnalysisRun.objects.filter(created_at__gte=start_date).count()
    
    # Daily analyses
    daily_analyses = AnalysisRun.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Transformations applied
    total_transformations = TransformationLog.objects.count()
    transformations_this_period = TransformationLog.objects.filter(
        applied_at__gte=start_date
    ).count()
    
    # Most common transformations
    common_actions = TransformationLog.objects.values('action').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return Response({
        'total_projects': total_projects,
        'projects_this_period': projects_this_period,
        'status_breakdown': list(status_breakdown),
        'source_breakdown': list(source_breakdown),
        'daily_projects': list(daily_projects),
        'total_rows_processed': total_rows,
        'avg_rows_per_project': round(avg_rows),
        'total_analyses': total_analyses,
        'analyses_this_period': analyses_this_period,
        'daily_analyses': list(daily_analyses),
        'total_transformations': total_transformations,
        'transformations_this_period': transformations_this_period,
        'common_actions': list(common_actions)
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def pipeline_analytics(request):
    """
    Scheduled pipeline analytics
    """
    now = timezone.now()
    days = int(request.query_params.get('days', 30))
    start_date = now - timedelta(days=days)
    
    # Pipeline counts
    total_pipelines = ScheduledPipeline.objects.count()
    active_pipelines = ScheduledPipeline.objects.filter(is_active=True).count()
    paused_pipelines = ScheduledPipeline.objects.filter(is_active=False).count()
    
    # Pipeline runs
    total_runs = PipelineRun.objects.count()
    runs_this_period = PipelineRun.objects.filter(started_at__gte=start_date).count()
    
    # Run status breakdown
    run_status = PipelineRun.objects.filter(
        started_at__gte=start_date
    ).values('status').annotate(
        count=Count('id')
    )
    
    # Success rate
    completed = PipelineRun.objects.filter(
        started_at__gte=start_date, status='completed'
    ).count()
    failed = PipelineRun.objects.filter(
        started_at__gte=start_date, status='failed'
    ).count()
    success_rate = round((completed / max(completed + failed, 1)) * 100, 1)
    
    # Daily runs
    daily_runs = PipelineRun.objects.filter(
        started_at__gte=start_date
    ).annotate(
        date=TruncDate('started_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Average duration
    avg_duration = PipelineRun.objects.filter(
        duration_seconds__isnull=False
    ).aggregate(avg=Avg('duration_seconds'))['avg'] or 0
    
    # Most active pipelines
    active_pipelines_list = ScheduledPipeline.objects.annotate(
        run_count_total=Count('runs')
    ).order_by('-run_count_total')[:10]
    
    return Response({
        'total_pipelines': total_pipelines,
        'active_pipelines': active_pipelines,
        'paused_pipelines': paused_pipelines,
        'total_runs': total_runs,
        'runs_this_period': runs_this_period,
        'run_status': list(run_status),
        'success_rate': success_rate,
        'daily_runs': list(daily_runs),
        'avg_duration_seconds': round(avg_duration),
        'top_pipelines': [{
            'name': p.name,
            'project': p.project.name,
            'run_count': p.run_count_total,
            'schedule_type': p.schedule_type,
            'is_active': p.is_active
        } for p in active_pipelines_list]
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def subscription_analytics(request):
    """
    Business analytics: subscriptions, revenue metrics
    """
    # Subscription breakdown
    subscription_counts = Subscription.objects.values('plan').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Status breakdown
    status_counts = Subscription.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Users by plan
    total_subs = Subscription.objects.count()
    
    # Conversion funnel (simplified - users who upgraded from free)
    free_users = Subscription.objects.filter(plan='free').count()
    paid_users = Subscription.objects.exclude(plan='free').count()
    conversion_rate = round((paid_users / max(total_subs, 1)) * 100, 1)
    
    return Response({
        'subscription_breakdown': list(subscription_counts),
        'status_breakdown': list(status_counts),
        'total_subscriptions': total_subs,
        'free_users': free_users,
        'paid_users': paid_users,
        'conversion_rate': conversion_rate
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def retention_analytics(request):
    """
    Retention analytics: cohort analysis, retention rates
    """
    now = timezone.now()
    
    # Cohort analysis - users grouped by signup month
    cohorts = User.objects.annotate(
        cohort=TruncMonth('date_joined')
    ).values('cohort').annotate(
        total_users=Count('id')
    ).order_by('-cohort')[:6]
    
    result = []
    for cohort in cohorts:
        cohort_date = cohort['cohort']
        cohort_users = User.objects.filter(
            date_joined__year=cohort_date.year,
            date_joined__month=cohort_date.month
        )
        
        total = cohort_users.count()
        
        # Check retention for each subsequent month
        retention_data = {'cohort': cohort_date.strftime('%Y-%m'), 'total': total}
        
        for month_offset in range(1, 4):  # Check 3 months ahead
            check_date = cohort_date + timedelta(days=30 * month_offset)
            if check_date <= now:
                active_count = cohort_users.filter(
                    last_login__gte=check_date - timedelta(days=30),
                    last_login__lt=check_date
                ).count()
                retention_data[f'month_{month_offset}'] = round((active_count / max(total, 1)) * 100, 1)
        
        result.append(retention_data)
    
    # Day 1, 7, 30 retention
    yesterday = now - timedelta(days=1)
    last_week = now - timedelta(days=7)
    last_month = now - timedelta(days=30)
    
    day1_cohort = User.objects.filter(date_joined__date=yesterday.date())
    day1_retained = day1_cohort.filter(last_login__date=now.date()).count()
    day1_retention = round((day1_retained / max(day1_cohort.count(), 1)) * 100, 1)
    
    day7_cohort = User.objects.filter(date_joined__date=last_week.date())
    day7_retained = day7_cohort.filter(last_login__gte=now - timedelta(days=1)).count()
    day7_retention = round((day7_retained / max(day7_cohort.count(), 1)) * 100, 1)
    
    day30_cohort = User.objects.filter(date_joined__date=last_month.date())
    day30_retained = day30_cohort.filter(last_login__gte=now - timedelta(days=7)).count()
    day30_retention = round((day30_retained / max(day30_cohort.count(), 1)) * 100, 1)
    
    return Response({
        'cohort_retention': result,
        'day1_retention': day1_retention,
        'day7_retention': day7_retention,
        'day30_retention': day30_retention
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def funnel_analytics(request):
    """
    Funnel analytics: user journey stages
    """
    total_users = User.objects.count()
    verified_users = User.objects.filter(is_verified=True).count()
    
    # Users with at least one project
    users_with_projects = User.objects.annotate(
        project_count=Count('projects')
    ).filter(project_count__gt=0).count()
    
    # Users with uploaded data
    users_with_data = User.objects.filter(
        projects__row_count__isnull=False
    ).distinct().count()
    
    # Users who analyzed data
    users_analyzed = User.objects.filter(
        projects__analyses__isnull=False
    ).distinct().count()
    
    # Users who applied transformations
    users_transformed = User.objects.filter(
        projects__transformations__isnull=False
    ).distinct().count()
    
    # Users with scheduled pipelines
    users_with_schedules = User.objects.filter(
        projects__schedules__isnull=False
    ).distinct().count()
    
    funnel = [
        {'stage': 'Signed Up', 'count': total_users, 'rate': 100},
        {'stage': 'Verified Email', 'count': verified_users, 
         'rate': round((verified_users / max(total_users, 1)) * 100, 1)},
        {'stage': 'Created Project', 'count': users_with_projects,
         'rate': round((users_with_projects / max(total_users, 1)) * 100, 1)},
        {'stage': 'Uploaded Data', 'count': users_with_data,
         'rate': round((users_with_data / max(total_users, 1)) * 100, 1)},
        {'stage': 'Ran Analysis', 'count': users_analyzed,
         'rate': round((users_analyzed / max(total_users, 1)) * 100, 1)},
        {'stage': 'Applied Transforms', 'count': users_transformed,
         'rate': round((users_transformed / max(total_users, 1)) * 100, 1)},
        {'stage': 'Scheduled Pipeline', 'count': users_with_schedules,
         'rate': round((users_with_schedules / max(total_users, 1)) * 100, 1)},
    ]
    
    return Response({'funnel': funnel})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def recent_activity_feed(request):
    """
    Real-time activity feed
    """
    limit = int(request.query_params.get('limit', 50))
    
    # Get recent usage tracking
    recent_usage = UsageTracking.objects.select_related('user').order_by('-timestamp')[:limit]
    
    activities = [{
        'id': str(u.tracking_id),
        'user_email': u.user.email,
        'user_name': u.user.name,
        'action': u.action,
        'resource_type': u.resource_type,
        'resource_id': str(u.resource_id) if u.resource_id else None,
        'metadata': u.metadata,
        'timestamp': u.timestamp.isoformat()
    } for u in recent_usage]
    
    return Response({'activities': activities})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_health(request):
    """
    System health metrics
    """
    from django.db import connection
    import time
    
    # Database response time
    start = time.time()
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    db_response_time = round((time.time() - start) * 1000, 2)
    
    # Get database stats
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM projects")
            total_projects = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
    except Exception:
        total_projects = Project.objects.count()
        total_users = User.objects.count()
    
    # Recent errors (from pipeline runs)
    now = timezone.now()
    recent_errors = PipelineRun.objects.filter(
        status='failed',
        started_at__gte=now - timedelta(hours=24)
    ).count()
    
    total_runs_24h = PipelineRun.objects.filter(
        started_at__gte=now - timedelta(hours=24)
    ).count()
    
    error_rate = round((recent_errors / max(total_runs_24h, 1)) * 100, 2)
    
    return Response({
        'db_response_ms': db_response_time,
        'total_projects': total_projects,
        'total_users': total_users,
        'errors_24h': recent_errors,
        'total_operations_24h': total_runs_24h,
        'error_rate': error_rate,
        'status': 'healthy' if error_rate < 5 else 'warning' if error_rate < 20 else 'critical'
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_summary(request):
    """
    Combined dashboard summary for quick overview
    """
    now = timezone.now()
    today = now.date()
    
    # User metrics
    total_users = User.objects.count()
    new_today = User.objects.filter(date_joined__date=today).count()
    active_today = User.objects.filter(last_login__date=today).count()
    
    # Project metrics  
    total_projects = Project.objects.count()
    new_projects_today = Project.objects.filter(created_at__date=today).count()
    
    # Pipeline metrics
    runs_today = PipelineRun.objects.filter(started_at__date=today).count()
    successful_today = PipelineRun.objects.filter(
        started_at__date=today, status='completed'
    ).count()
    failed_today = PipelineRun.objects.filter(
        started_at__date=today, status='failed'
    ).count()
    
    # Data processed
    total_rows = Project.objects.aggregate(total=Sum('row_count'))['total'] or 0
    
    # Subscriptions
    subscription_breakdown = list(
        Subscription.objects.values('plan').annotate(count=Count('id'))
    )
    
    return Response({
        'users': {
            'total': total_users,
            'new_today': new_today,
            'active_today': active_today
        },
        'projects': {
            'total': total_projects,
            'new_today': new_projects_today,
            'total_rows': total_rows
        },
        'pipelines': {
            'runs_today': runs_today,
            'successful': successful_today,
            'failed': failed_today
        },
        'subscriptions': subscription_breakdown
    })
