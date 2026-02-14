from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.http import FileResponse
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os
from projects.models import Project
from .models import Export

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_data(request, project_id):
    export_format = request.query_params.get('format', 'csv')
    
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    file_path = project.processed_file_path or project.file_path
    if not file_path:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        
        export_path = os.path.join(settings.PIPELINE_STORAGE_PATH, 'exports', f"{project_id}_export")
        
        if export_format == 'csv':
            export_path += '.csv'
            df.to_csv(export_path, index=False)
        elif export_format == 'xlsx':
            export_path += '.xlsx'
            df.to_excel(export_path, index=False)
        elif export_format == 'json':
            export_path += '.json'
            df.to_json(export_path, orient='records', indent=2)
        
        file_size = os.path.getsize(export_path)
        
        Export.objects.create(
            project=project,
            export_type=export_format,
            file_path=export_path,
            file_size=file_size
        )
        
        return FileResponse(
            open(export_path, 'rb'),
            as_attachment=True,
            filename=f"{project.name}_export.{export_format}"
        )
    
    except Exception as e:
        return Response({'detail': f'Export failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_charts(request, project_id):
    chart_type = request.query_params.get('type', 'summary')
    
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    file_path = project.processed_file_path or project.file_path
    if not file_path:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        
        charts = []
        
        if chart_type == 'summary' or chart_type == 'all':
            numeric_cols = df.select_dtypes(include=['number']).columns[:5]
            
            for col in numeric_cols:
                fig = px.histogram(df, x=col, title=f'Distribution of {col}')
                chart_html = fig.to_html(include_plotlyjs='cdn')
                charts.append({
                    'title': f'Distribution of {col}',
                    'type': 'histogram',
                    'html': chart_html
                })
            
            categorical_cols = df.select_dtypes(include=['object']).columns[:3]
            for col in categorical_cols:
                value_counts = df[col].value_counts().head(10)
                fig = px.bar(x=value_counts.index, y=value_counts.values, 
                           title=f'Top values in {col}', labels={'x': col, 'y': 'Count'})
                chart_html = fig.to_html(include_plotlyjs='cdn')
                charts.append({
                    'title': f'Top values in {col}',
                    'type': 'bar',
                    'html': chart_html
                })
        
        if chart_type == 'correlation' or chart_type == 'all':
            numeric_df = df.select_dtypes(include=['number'])
            if len(numeric_df.columns) > 1:
                corr = numeric_df.corr()
                fig = px.imshow(corr, text_auto=True, title='Correlation Heatmap',
                              labels=dict(color="Correlation"))
                chart_html = fig.to_html(include_plotlyjs='cdn')
                charts.append({
                    'title': 'Correlation Heatmap',
                    'type': 'heatmap',
                    'html': chart_html
                })
        
        if chart_type == 'missing' or chart_type == 'all':
            missing = df.isnull().sum()
            missing = missing[missing > 0].sort_values(ascending=False)
            if len(missing) > 0:
                fig = px.bar(x=missing.index, y=missing.values,
                           title='Missing Values by Column',
                           labels={'x': 'Column', 'y': 'Missing Count'})
                chart_html = fig.to_html(include_plotlyjs='cdn')
                charts.append({
                    'title': 'Missing Values',
                    'type': 'bar',
                    'html': chart_html
                })
        
        return Response({'charts': charts})
    
    except Exception as e:
        return Response({'detail': f'Chart generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)