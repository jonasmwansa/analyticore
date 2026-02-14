from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Avg
from datetime import timedelta
from croniter import croniter
import logging

from .models import ScheduledPipeline, PipelineRun
from .tasks import execute_scheduled_pipeline, run_pipeline_manually
from projects.models import Project

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_schedules(request):
    """List all scheduled pipelines for the user"""
    schedules = ScheduledPipeline.objects.filter(user=request.user).select_related('project')
    
    # Get run statistics
    data = []
    for schedule in schedules:
        recent_runs = schedule.runs.order_by('-started_at')[:5]
        success_rate = schedule.runs.filter(status='completed').count()
        total_runs = schedule.run_count or 1
        
        data.append({
            'schedule_id': str(schedule.schedule_id),
            'name': schedule.name,
            'description': schedule.description,
            'project': {
                'id': str(schedule.project.project_id),
                'name': schedule.project.name
            },
            'schedule_type': schedule.schedule_type,
            'action_type': schedule.action_type,
            'is_active': schedule.is_active,
            'status': schedule.status,
            'schedule_display': get_schedule_display(schedule),
            'last_run': schedule.last_run.isoformat() if schedule.last_run else None,
            'next_run': calculate_next_run(schedule),
            'run_count': schedule.run_count,
            'success_rate': round((success_rate / total_runs) * 100, 1) if total_runs > 0 else 0,
            'recent_runs': [{
                'run_id': str(run.run_id),
                'status': run.status,
                'started_at': run.started_at.isoformat(),
                'duration_seconds': run.duration_seconds,
                'trigger': run.trigger
            } for run in recent_runs],
            'created_at': schedule.created_at.isoformat()
        })
    
    return Response({'schedules': data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_schedule(request):
    """Create a new scheduled pipeline"""
    project_id = request.data.get('project_id')
    name = request.data.get('name')
    
    if not project_id or not name:
        return Response({'error': 'project_id and name are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Validate schedule type
    schedule_type = request.data.get('schedule_type', 'daily')
    if schedule_type not in dict(ScheduledPipeline.SCHEDULE_TYPES):
        return Response({'error': 'Invalid schedule type'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate action type
    action_type = request.data.get('action_type', 'run_analysis')
    if action_type not in dict(ScheduledPipeline.ACTION_TYPES):
        return Response({'error': 'Invalid action type'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create schedule
    schedule = ScheduledPipeline.objects.create(
        user=request.user,
        project=project,
        name=name,
        description=request.data.get('description', ''),
        schedule_type=schedule_type,
        hour=int(request.data.get('hour', 0)),
        minute=int(request.data.get('minute', 0)),
        day_of_week=request.data.get('day_of_week', '*'),
        day_of_month=request.data.get('day_of_month', '*'),
        cron_expression=request.data.get('cron_expression', ''),
        action_type=action_type,
        pipeline_config=request.data.get('pipeline_config', {}),
        is_active=request.data.get('is_active', True)
    )
    
    # Create Celery Beat task
    try:
        schedule.sync_celery_task()
    except Exception as e:
        logger.error(f"Failed to create Celery task: {str(e)}")
    
    return Response({
        'schedule_id': str(schedule.schedule_id),
        'name': schedule.name,
        'message': 'Schedule created successfully',
        'next_run': calculate_next_run(schedule)
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_schedule(request, schedule_id):
    """Get details of a specific schedule"""
    try:
        schedule = ScheduledPipeline.objects.select_related('project').get(
            schedule_id=schedule_id,
            user=request.user
        )
    except ScheduledPipeline.DoesNotExist:
        return Response({'error': 'Schedule not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get run history
    runs = schedule.runs.order_by('-started_at')[:20]
    
    return Response({
        'schedule_id': str(schedule.schedule_id),
        'name': schedule.name,
        'description': schedule.description,
        'project': {
            'id': str(schedule.project.project_id),
            'name': schedule.project.name,
            'status': schedule.project.status
        },
        'schedule_type': schedule.schedule_type,
        'hour': schedule.hour,
        'minute': schedule.minute,
        'day_of_week': schedule.day_of_week,
        'day_of_month': schedule.day_of_month,
        'cron_expression': schedule.cron_expression,
        'action_type': schedule.action_type,
        'pipeline_config': schedule.pipeline_config,
        'is_active': schedule.is_active,
        'status': schedule.status,
        'schedule_display': get_schedule_display(schedule),
        'last_run': schedule.last_run.isoformat() if schedule.last_run else None,
        'next_run': calculate_next_run(schedule),
        'run_count': schedule.run_count,
        'consecutive_failures': schedule.consecutive_failures,
        'runs': [{
            'run_id': str(run.run_id),
            'status': run.status,
            'trigger': run.trigger,
            'started_at': run.started_at.isoformat(),
            'completed_at': run.completed_at.isoformat() if run.completed_at else None,
            'duration_seconds': run.duration_seconds,
            'rows_processed': run.rows_processed,
            'error_message': run.error_message[:200] if run.error_message else None
        } for run in runs],
        'created_at': schedule.created_at.isoformat(),
        'updated_at': schedule.updated_at.isoformat()
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_schedule(request, schedule_id):
    """Update a scheduled pipeline"""
    try:
        schedule = ScheduledPipeline.objects.get(schedule_id=schedule_id, user=request.user)
    except ScheduledPipeline.DoesNotExist:
        return Response({'error': 'Schedule not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Update fields
    if 'name' in request.data:
        schedule.name = request.data['name']
    if 'description' in request.data:
        schedule.description = request.data['description']
    if 'schedule_type' in request.data:
        schedule.schedule_type = request.data['schedule_type']
    if 'hour' in request.data:
        schedule.hour = int(request.data['hour'])
    if 'minute' in request.data:
        schedule.minute = int(request.data['minute'])
    if 'day_of_week' in request.data:
        schedule.day_of_week = request.data['day_of_week']
    if 'day_of_month' in request.data:
        schedule.day_of_month = request.data['day_of_month']
    if 'cron_expression' in request.data:
        schedule.cron_expression = request.data['cron_expression']
    if 'action_type' in request.data:
        schedule.action_type = request.data['action_type']
    if 'pipeline_config' in request.data:
        schedule.pipeline_config = request.data['pipeline_config']
    if 'is_active' in request.data:
        schedule.is_active = request.data['is_active']
    
    # Reset status if reactivating
    if request.data.get('is_active') and schedule.status == 'failed':
        schedule.status = 'active'
        schedule.consecutive_failures = 0
    
    schedule.save()
    
    # Update Celery Beat task
    try:
        schedule.sync_celery_task()
    except Exception as e:
        logger.error(f"Failed to update Celery task: {str(e)}")
    
    return Response({
        'schedule_id': str(schedule.schedule_id),
        'message': 'Schedule updated successfully',
        'next_run': calculate_next_run(schedule)
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_schedule(request, schedule_id):
    """Delete a scheduled pipeline"""
    try:
        schedule = ScheduledPipeline.objects.get(schedule_id=schedule_id, user=request.user)
    except ScheduledPipeline.DoesNotExist:
        return Response({'error': 'Schedule not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Delete Celery Beat task
    schedule.delete_celery_task()
    
    # Delete schedule (runs will be cascaded)
    schedule.delete()
    
    return Response({'message': 'Schedule deleted successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_schedule(request, schedule_id):
    """Toggle schedule active/paused state"""
    try:
        schedule = ScheduledPipeline.objects.get(schedule_id=schedule_id, user=request.user)
    except ScheduledPipeline.DoesNotExist:
        return Response({'error': 'Schedule not found'}, status=status.HTTP_404_NOT_FOUND)
    
    schedule.is_active = not schedule.is_active
    
    # Reset status if reactivating
    if schedule.is_active and schedule.status == 'paused':
        schedule.status = 'active'
    elif not schedule.is_active:
        schedule.status = 'paused'
    
    schedule.save()
    
    # Update Celery Beat task
    try:
        schedule.sync_celery_task()
    except Exception as e:
        logger.error(f"Failed to toggle Celery task: {str(e)}")
    
    return Response({
        'schedule_id': str(schedule.schedule_id),
        'is_active': schedule.is_active,
        'status': schedule.status,
        'message': f"Schedule {'activated' if schedule.is_active else 'paused'}"
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_now(request, schedule_id):
    """Trigger an immediate run of a scheduled pipeline"""
    try:
        schedule = ScheduledPipeline.objects.get(schedule_id=schedule_id, user=request.user)
    except ScheduledPipeline.DoesNotExist:
        return Response({'error': 'Schedule not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Create a pending run record
    run = PipelineRun.objects.create(
        scheduled_pipeline=schedule,
        status='pending',
        trigger='manual'
    )
    
    # Try to queue the task, if Celery/Redis is available
    # Otherwise, run synchronously
    try:
        execute_scheduled_pipeline.delay(str(schedule.schedule_id))
        return Response({
            'message': 'Pipeline run queued',
            'run_id': str(run.run_id),
            'status': 'pending'
        })
    except Exception as e:
        # Celery not available, run synchronously
        logger.warning(f"Celery not available, running synchronously: {str(e)}")
        try:
            result = execute_scheduled_pipeline(str(schedule.schedule_id))
            return Response({
                'message': 'Pipeline run completed',
                'run_id': str(run.run_id),
                'status': result.get('status', 'completed'),
                'duration': result.get('duration'),
                'rows_processed': result.get('rows_processed')
            })
        except Exception as run_error:
            run.status = 'failed'
            run.error_message = str(run_error)
            run.save()
            return Response({
                'message': 'Pipeline run failed',
                'run_id': str(run.run_id),
                'error': str(run_error)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_run_details(request, run_id):
    """Get details of a specific pipeline run"""
    try:
        run = PipelineRun.objects.select_related('scheduled_pipeline', 'scheduled_pipeline__project').get(
            run_id=run_id,
            scheduled_pipeline__user=request.user
        )
    except PipelineRun.DoesNotExist:
        return Response({'error': 'Run not found'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'run_id': str(run.run_id),
        'schedule': {
            'id': str(run.scheduled_pipeline.schedule_id),
            'name': run.scheduled_pipeline.name
        },
        'project': {
            'id': str(run.scheduled_pipeline.project.project_id),
            'name': run.scheduled_pipeline.project.name
        },
        'status': run.status,
        'trigger': run.trigger,
        'started_at': run.started_at.isoformat(),
        'completed_at': run.completed_at.isoformat() if run.completed_at else None,
        'duration_seconds': run.duration_seconds,
        'rows_processed': run.rows_processed,
        'transformations_applied': run.transformations_applied,
        'output_file': run.output_file,
        'logs': run.logs,
        'error_message': run.error_message
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_run_history(request):
    """Get all pipeline runs for the user"""
    runs = PipelineRun.objects.filter(
        scheduled_pipeline__user=request.user
    ).select_related('scheduled_pipeline', 'scheduled_pipeline__project').order_by('-started_at')[:50]
    
    return Response({
        'runs': [{
            'run_id': str(run.run_id),
            'schedule': {
                'id': str(run.scheduled_pipeline.schedule_id),
                'name': run.scheduled_pipeline.name
            },
            'project_name': run.scheduled_pipeline.project.name,
            'status': run.status,
            'trigger': run.trigger,
            'started_at': run.started_at.isoformat(),
            'duration_seconds': run.duration_seconds,
            'rows_processed': run.rows_processed,
            'error_message': run.error_message[:100] if run.error_message else None
        } for run in runs]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_schedule_stats(request):
    """Get aggregated statistics for scheduled pipelines"""
    schedules = ScheduledPipeline.objects.filter(user=request.user)
    
    total_schedules = schedules.count()
    active_schedules = schedules.filter(is_active=True, status='active').count()
    
    # Run statistics for last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_runs = PipelineRun.objects.filter(
        scheduled_pipeline__user=request.user,
        started_at__gte=seven_days_ago
    )
    
    total_runs = recent_runs.count()
    successful_runs = recent_runs.filter(status='completed').count()
    failed_runs = recent_runs.filter(status='failed').count()
    avg_duration = recent_runs.filter(duration_seconds__isnull=False).aggregate(
        avg=Avg('duration_seconds')
    )['avg']
    
    # Runs per day
    runs_by_day = []
    for i in range(7):
        day = timezone.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = recent_runs.filter(started_at__gte=day_start, started_at__lt=day_end).count()
        runs_by_day.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'count': count
        })
    
    return Response({
        'total_schedules': total_schedules,
        'active_schedules': active_schedules,
        'paused_schedules': total_schedules - active_schedules,
        'runs_last_7_days': {
            'total': total_runs,
            'successful': successful_runs,
            'failed': failed_runs,
            'success_rate': round((successful_runs / total_runs) * 100, 1) if total_runs > 0 else 0,
            'avg_duration_seconds': round(avg_duration, 1) if avg_duration else 0
        },
        'runs_by_day': list(reversed(runs_by_day))
    })


def get_schedule_display(schedule):
    """Generate human-readable schedule display"""
    if schedule.schedule_type == 'hourly':
        return f"Every hour at minute {schedule.minute}"
    elif schedule.schedule_type == 'daily':
        return f"Daily at {schedule.hour:02d}:{schedule.minute:02d}"
    elif schedule.schedule_type == 'weekly':
        days = {'0': 'Sunday', '1': 'Monday', '2': 'Tuesday', '3': 'Wednesday', 
                '4': 'Thursday', '5': 'Friday', '6': 'Saturday', '*': 'Every day'}
        day_name = days.get(schedule.day_of_week, schedule.day_of_week)
        return f"Every {day_name} at {schedule.hour:02d}:{schedule.minute:02d}"
    elif schedule.schedule_type == 'monthly':
        return f"Monthly on day {schedule.day_of_month} at {schedule.hour:02d}:{schedule.minute:02d}"
    elif schedule.schedule_type == 'custom':
        return f"Custom: {schedule.cron_expression}"
    return "Unknown"


def calculate_next_run(schedule):
    """Calculate the next run time for a schedule"""
    if not schedule.is_active or schedule.status != 'active':
        return None
    
    try:
        # Build cron expression
        if schedule.schedule_type == 'hourly':
            cron = f"{schedule.minute} * * * *"
        elif schedule.schedule_type == 'daily':
            cron = f"{schedule.minute} {schedule.hour} * * *"
        elif schedule.schedule_type == 'weekly':
            cron = f"{schedule.minute} {schedule.hour} * * {schedule.day_of_week}"
        elif schedule.schedule_type == 'monthly':
            cron = f"{schedule.minute} {schedule.hour} {schedule.day_of_month} * *"
        elif schedule.schedule_type == 'custom' and schedule.cron_expression:
            cron = schedule.cron_expression
        else:
            return None
        
        iter = croniter(cron, timezone.now())
        next_run = iter.get_next(timezone.datetime)
        return next_run.isoformat()
    except Exception as e:
        logger.error(f"Failed to calculate next run: {str(e)}")
        return None
