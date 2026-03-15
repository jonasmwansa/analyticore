"""
Pipeline Views - API endpoints for automated analysis pipeline
"""
import pandas as pd
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from projects.models import Project
from .models import PipelineProgress
from .pipeline_runner import (
    start_pipeline, run_pipeline, get_pipeline_status,
    PipelineRunner
)
from .local_llm_service import get_llm_status


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_pipeline_view(request, project_id):
    """Start automated analysis pipeline for a project"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not project.file_path:
        return Response({'detail': 'No data uploaded yet'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if there's already a running pipeline
    existing = PipelineProgress.objects.filter(
        project=project,
        status__in=['pending', 'running', 'paused']
    ).first()
    
    if existing:
        return Response({
            'detail': 'A pipeline is already running for this project',
            'pipeline_id': str(existing.pipeline_id),
            'status': existing.status
        }, status=status.HTTP_409_CONFLICT)
    
    # Load dataframe
    try:
        file_path = project.processed_file_path or project.file_path
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            return Response({'detail': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': f'Failed to load data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Get LLM preference
    llm_enabled = request.data.get('llm_enabled', True)
    
    # Create pipeline progress
    progress = start_pipeline(project, df, request.user, llm_enabled=llm_enabled)
    
    # Run pipeline synchronously (for simplicity - can be made async with Celery)
    # In production, you'd want: run_pipeline_task.delay(str(progress.pipeline_id))
    try:
        result = run_pipeline(progress, df, project)
    except Exception as e:
        progress.status = 'failed'
        progress.error_message = str(e)
        progress.save()
        return Response({
            'pipeline_id': str(progress.pipeline_id),
            'status': 'failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'pipeline_id': str(progress.pipeline_id),
        'status': result.get('status', 'unknown'),
        'message': 'Pipeline completed' if result.get('status') == 'completed' else result.get('message'),
        'results': result.get('results') if result.get('status') == 'completed' else None
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pipeline_status_view(request, pipeline_id):
    """Get current status of a pipeline"""
    try:
        progress = PipelineProgress.objects.select_related('project').get(
            pipeline_id=pipeline_id,
            user=request.user
        )
    except PipelineProgress.DoesNotExist:
        return Response({'detail': 'Pipeline not found'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'pipeline_id': str(progress.pipeline_id),
        'project_id': str(progress.project.project_id),
        'project_name': progress.project.name,
        'status': progress.status,
        'current_stage': progress.current_stage,
        'progress_percent': progress.progress_percent,
        'stages_completed': progress.stages_completed,
        'current_stage_data': progress.current_stage_data,
        'llm_enabled': progress.llm_enabled,
        'llm_insights': progress.llm_insights,
        'error_message': progress.error_message,
        'started_at': progress.started_at.isoformat() if progress.started_at else None,
        'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
        'duration_seconds': progress.duration_seconds,
        'cancel_requested': progress.cancel_requested,
        'pause_requested': progress.pause_requested,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_pipeline(request, pipeline_id):
    """Cancel a running pipeline"""
    try:
        progress = PipelineProgress.objects.get(
            pipeline_id=pipeline_id,
            user=request.user
        )
    except PipelineProgress.DoesNotExist:
        return Response({'detail': 'Pipeline not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if progress.status not in ['pending', 'running', 'paused']:
        return Response({
            'detail': f'Pipeline cannot be cancelled (status: {progress.status})'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    progress.request_cancel()
    
    return Response({
        'message': 'Cancel request sent',
        'pipeline_id': str(progress.pipeline_id),
        'status': progress.status
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pause_pipeline(request, pipeline_id):
    """Pause a running pipeline"""
    try:
        progress = PipelineProgress.objects.get(
            pipeline_id=pipeline_id,
            user=request.user
        )
    except PipelineProgress.DoesNotExist:
        return Response({'detail': 'Pipeline not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if progress.status != 'running':
        return Response({
            'detail': f'Pipeline cannot be paused (status: {progress.status})'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    progress.request_pause()
    
    return Response({
        'message': 'Pause request sent',
        'pipeline_id': str(progress.pipeline_id),
        'status': progress.status
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resume_pipeline(request, pipeline_id):
    """Resume a paused pipeline"""
    try:
        progress = PipelineProgress.objects.get(
            pipeline_id=pipeline_id,
            user=request.user
        )
    except PipelineProgress.DoesNotExist:
        return Response({'detail': 'Pipeline not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if progress.status != 'paused':
        return Response({
            'detail': f'Pipeline cannot be resumed (status: {progress.status})'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Load dataframe and continue
    try:
        project = progress.project
        file_path = project.processed_file_path or project.file_path
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            return Response({'detail': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
        
        progress.resume()
        result = run_pipeline(progress, df, project)
        
        return Response({
            'message': 'Pipeline resumed',
            'pipeline_id': str(progress.pipeline_id),
            'status': result.get('status', 'unknown'),
            'results': result.get('results') if result.get('status') == 'completed' else None
        })
        
    except Exception as e:
        return Response({
            'detail': f'Failed to resume pipeline: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pipeline_results(request, pipeline_id):
    """Get full results of a completed pipeline"""
    try:
        progress = PipelineProgress.objects.select_related('project').get(
            pipeline_id=pipeline_id,
            user=request.user
        )
    except PipelineProgress.DoesNotExist:
        return Response({'detail': 'Pipeline not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if progress.status != 'completed':
        return Response({
            'detail': f'Pipeline not completed (status: {progress.status})',
            'status': progress.status,
            'progress_percent': progress.progress_percent
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'pipeline_id': str(progress.pipeline_id),
        'project_id': str(progress.project.project_id),
        'project_name': progress.project.name,
        'status': 'completed',
        'duration_seconds': progress.duration_seconds,
        'stages': progress.stages_completed,
        'results': progress.final_results,
        'llm_insights': progress.llm_insights,
        'completed_at': progress.completed_at.isoformat() if progress.completed_at else None
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_llm_status_view(request):
    """Get status of local LLM service"""
    llm_status = get_llm_status()
    return Response(llm_status)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_project_pipelines(request, project_id):
    """List all pipeline runs for a project"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    pipelines = PipelineProgress.objects.filter(project=project).order_by('-created_at')[:20]
    
    return Response({
        'project_id': str(project_id),
        'pipelines': [
            {
                'pipeline_id': str(p.pipeline_id),
                'status': p.status,
                'current_stage': p.current_stage,
                'progress_percent': p.progress_percent,
                'started_at': p.started_at.isoformat() if p.started_at else None,
                'completed_at': p.completed_at.isoformat() if p.completed_at else None,
                'duration_seconds': p.duration_seconds,
            }
            for p in pipelines
        ]
    })
