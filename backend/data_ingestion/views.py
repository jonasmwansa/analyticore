from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.utils import timezone
import pandas as pd
import numpy as np
import os
from projects.models import Project
from .models import DataSource, DataUpload
from pipelines.context import PipelineContext
from pipelines.base import Pipeline
from pipelines.steps import ColumnUnderstandingStep


def convert_to_serializable(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(v) for v in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj) if not np.isnan(obj) else None
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif pd.isna(obj):
        return None
    return obj

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
        
        context = PipelineContext(
            project_id=str(project_id),
            original_df=df.copy(),
            current_df=df.copy()
        )
        
        pipeline = Pipeline("Column Understanding")
        pipeline.add_step(ColumnUnderstandingStep())
        context = pipeline.execute(context)
        
        statistics = {
            'total_rows': int(len(df)),
            'total_columns': int(len(df.columns)),
            'columns': df.columns.tolist(),
            'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'missing_values': {col: int(v) for col, v in df.isnull().sum().items()},
            'sample_data': convert_to_serializable(df.head(5).to_dict('records')),
            'column_metadata': {name: convert_to_serializable({
                'inferred_type': meta.inferred_type,
                'confidence': meta.confidence,
                'missing_percentage': meta.missing_percentage,
                'unique_count': meta.unique_count,
                'is_identifier': meta.is_identifier,
                'statistics': meta.statistics
            }) for name, meta in context.metadata.items()}
        }
        
        project.original_filename = filename
        project.file_path = file_path
        project.row_count = len(df)
        project.column_count = len(df.columns)
        project.status = 'uploaded'
        project.statistics = statistics
        project.save()
        
        return Response({'message': 'File uploaded successfully', 'statistics': statistics})
    
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
        
        return Response({'data': df.head(100).to_dict('records'), 'total_rows': len(df), 'columns': df.columns.tolist()})
    except Exception as e:
        return Response({'detail': f'Failed to load data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
