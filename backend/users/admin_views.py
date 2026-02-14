from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from users.models import User
from users.saas_models import Subscription, UsageTracking
from projects.models import Project

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard_stats(request):
    total_users = User.objects.count()
    verified_users = User.objects.filter(is_verified=True).count()
    total_projects = Project.objects.count()
    
    last_30_days = timezone.now() - timedelta(days=30)
    new_users_30d = User.objects.filter(date_joined__gte=last_30_days).count()
    new_projects_30d = Project.objects.filter(created_at__gte=last_30_days).count()
    
    subscription_breakdown = Subscription.objects.values('plan').annotate(count=Count('plan'))
    
    project_status_breakdown = Project.objects.values('status').annotate(count=Count('status'))
    
    top_users = User.objects.annotate(
        project_count=Count('projects')
    ).order_by('-project_count')[:10]
    
    recent_activity = UsageTracking.objects.select_related('user').order_by('-timestamp')[:50]
    
    return Response({
        'overview': {
            'total_users': total_users,
            'verified_users': verified_users,
            'total_projects': total_projects,
            'new_users_30d': new_users_30d,
            'new_projects_30d': new_projects_30d,
        },
        'subscriptions': list(subscription_breakdown),
        'project_statuses': list(project_status_breakdown),
        'top_users': [{
            'email': u.email,
            'name': u.name,
            'project_count': u.project_count,
            'date_joined': u.date_joined
        } for u in top_users],
        'recent_activity': [{
            'user': a.user.email,
            'action': a.action,
            'resource_type': a.resource_type,
            'timestamp': a.timestamp
        } for a in recent_activity]
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users_list(request):
    users = User.objects.annotate(
        project_count=Count('projects')
    ).order_by('-date_joined')[:100]
    
    return Response({
        'users': [{
            'user_id': str(u.user_id),
            'email': u.email,
            'name': u.name,
            'is_verified': u.is_verified,
            'date_joined': u.date_joined,
            'project_count': u.project_count,
            'subscription': getattr(u.subscription, 'plan', 'free') if hasattr(u, 'subscription') else 'free'
        } for u in users]
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_projects_list(request):
    projects = Project.objects.select_related('user').order_by('-created_at')[:100]
    
    return Response({
        'projects': [{
            'project_id': str(p.project_id),
            'name': p.name,
            'user_email': p.user.email,
            'status': p.status,
            'source_type': p.source_type,
            'row_count': p.row_count,
            'column_count': p.column_count,
            'created_at': p.created_at,
        } for p in projects]
    })