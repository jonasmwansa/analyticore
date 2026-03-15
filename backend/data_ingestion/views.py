from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.utils import timezone
import pandas as pd
import os
from projects.models import Project
from .models import DataSource, DataUpload
from pipelines.tasks import clean_data_upload
from analysis.services import AutomatedAnalysisService


def _parse_boolean(value, default=True):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() not in {'0', 'false', 'no', 'off'}

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request, project_id):
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if 'file' not in request.FILES:
        return Response({'detail': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    filename = file.name
    
    file_path = os.path.join(settings.PIPELINE_STORAGE_PATH, 'original', f"{project_id}_{filename}")
    
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif filename.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            return Response({'detail': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
        project.original_filename = filename
        project.file_path = file_path
        project.status = 'uploaded'
        project.save()

        result = AutomatedAnalysisService.run(
            project,
            df,
            actor=request.user,
            auto_apply_cleaning=_parse_boolean(request.data.get('auto_apply_cleaning'), default=True),
            source='upload',
        )

        return Response({
            'message': 'File uploaded and automated analysis completed successfully',
            'statistics': result['statistics'],
            'recommendations': result['recommendations'],
            'automation': result['automation'],
        })
    
    except Exception as e:
        return Response({'detail': f'Failed to process file: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_data_preview(request, project_id):
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not project.file_path:
        return Response({'detail': 'No data uploaded yet'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        file_path = project.processed_file_path or project.file_path
        
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        
        preview_df = df.head(100)
        data_records = []
        for _, row in preview_df.iterrows():
            record = {}
            for col in preview_df.columns:
                val = row[col]
                if pd.isna(val):
                    record[col] = None
                elif hasattr(val, 'item'):
                    record[col] = val.item()
                else:
                    record[col] = val
            data_records.append(record)
        
        return Response({
            'data': data_records, 
            'total_rows': int(len(df)), 
            'columns': df.columns.tolist()
        })
    except Exception as e:
        return Response({'detail': f'Failed to load data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_clean_upload(request, upload_id):
    """Trigger cleaning for a specific DataUpload (runs async Celery task)."""
    try:
        upload = DataUpload.objects.select_related('data_source', 'user').get(id=upload_id)
    except DataUpload.DoesNotExist:
        return Response({'detail': 'Upload not found'}, status=status.HTTP_404_NOT_FOUND)

    # Only owner may trigger cleaning
    if upload.user != request.user:
        return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    # Prevent duplicate concurrent processing
    if upload.status == 'processing':
        return Response({'detail': 'Upload is already being processed'}, status=status.HTTP_400_BAD_REQUEST)

    # Mark as processing and schedule task
    upload.status = 'processing'
    upload.processed_at = timezone.now()
    upload.save()

    task = clean_data_upload.delay(str(upload.id))

    return Response({'message': 'Cleaning scheduled', 'task_id': task.id})
