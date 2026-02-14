from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import pandas as pd
import os
from projects.models import Project
from .models import AnalysisRun, TransformationLog
from pipelines.context import PipelineContext
from pipelines.base import Pipeline
from pipelines.steps import ColumnUnderstandingStep
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_data(request, project_id):
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not project.file_path:
        return Response({'detail': 'No data uploaded'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        if project.file_path.endswith('.csv'):
            df = pd.read_csv(project.file_path)
        elif project.file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(project.file_path)
        elif project.file_path.endswith('.json'):
            df = pd.read_json(project.file_path)
        
        analysis_prompt = f"""
You are a data cleaning expert. Analyze this dataset and provide actionable recommendations.

Dataset Info:
- Total Rows: {len(df)}
- Total Columns: {len(df.columns)}
- Columns: {', '.join(df.columns.tolist())}
- Data Types: {df.dtypes.to_dict()}
- Missing Values: {df.isnull().sum().to_dict()}
- Duplicate Rows: {df.duplicated().sum()}

For numeric columns:
{df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else 'No numeric columns'}

Provide recommendations in JSON format as an array of objects with these fields:
- column: column name
- issue: what's the problem
- recommendation: what to do
- action_type: one of [fill_missing, remove_duplicates, convert_type, remove_outliers, rename_column]
- parameters: object with action-specific parameters

Focus on:
1. Missing values (suggest mean/median/mode/forward-fill based on data type)
2. Data type conversions (dates, numbers stored as strings)
3. Outliers in numeric columns
4. Duplicate rows
5. Column naming improvements

Return ONLY valid JSON array, no additional text.
"""
        
        chat = LlmChat(
            api_key=settings.EMERGENT_LLM_KEY,
            session_id=f"analysis_{project_id}",
            system_message="You are a data analysis expert. Always respond with valid JSON."
        )
        chat.with_model("openai", "gpt-5.2")
        
        message = UserMessage(text=analysis_prompt)
        response = await chat.send_message(message)
        
        try:
            recommendations = json.loads(response)
        except:
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            recommendations = json.loads(response_clean.strip())
        
        analysis = AnalysisRun.objects.create(
            project=project,
            recommendations=recommendations,
            statistics=project.statistics
        )
        
        project.ai_recommendations = recommendations
        project.status = 'analyzed'
        project.save()
        
        return Response({'recommendations': recommendations})
    
    except Exception as e:
        return Response({'detail': f'Analysis failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_transformations(request, project_id):
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    rules = request.data.get('rules', [])
    if not rules:
        return Response({'detail': 'No transformation rules provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        file_path = project.file_path
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        
        original_shape = df.shape
        
        for rule in rules:
            column = rule.get('column')
            action = rule.get('action')
            params = rule.get('parameters', {})
            
            if action == 'fill_missing':
                strategy = params.get('strategy', 'mean')
                if strategy == 'mean' and df[column].dtype in ['int64', 'float64']:
                    df[column].fillna(df[column].mean(), inplace=True)
                elif strategy == 'median' and df[column].dtype in ['int64', 'float64']:
                    df[column].fillna(df[column].median(), inplace=True)
                elif strategy == 'mode':
                    df[column].fillna(df[column].mode()[0] if len(df[column].mode()) > 0 else 0, inplace=True)
                elif strategy == 'forward_fill':
                    df[column].fillna(method='ffill', inplace=True)
                elif strategy == 'constant':
                    df[column].fillna(params.get('value', 0), inplace=True)
            
            elif action == 'remove_duplicates':
                df.drop_duplicates(inplace=True)
            
            elif action == 'convert_type':
                target_type = params.get('target_type')
                if target_type == 'numeric':
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                elif target_type == 'datetime':
                    df[column] = pd.to_datetime(df[column], errors='coerce')
                elif target_type == 'string':
                    df[column] = df[column].astype(str)
            
            elif action == 'remove_outliers':
                if df[column].dtype in ['int64', 'float64']:
                    Q1 = df[column].quantile(0.25)
                    Q3 = df[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower = Q1 - 1.5 * IQR
                    upper = Q3 + 1.5 * IQR
                    df = df[(df[column] >= lower) & (df[column] <= upper)]
            
            elif action == 'rename_column':
                new_name = params.get('new_name')
                if new_name:
                    df.rename(columns={column: new_name}, inplace=True)
            
            TransformationLog.objects.create(
                project=project,
                step_name='User Applied',
                action=action,
                target=column,
                reason=rule.get('recommendation', 'User applied transformation'),
                impact={'before': original_shape, 'after': df.shape},
                confidence=1.0
            )
        
        processed_path = os.path.join(
            settings.PIPELINE_STORAGE_PATH,
            'processed',
            f"{project_id}_processed.csv"
        )
        df.to_csv(processed_path, index=False)
        
        project.processed_file_path = processed_path
        project.status = 'transformed'
        project.applied_transformations = rules
        project.save()
        
        return Response({
            'message': 'Transformations applied successfully',
            'original_shape': original_shape,
            'new_shape': df.shape,
            'processed_file': processed_path
        })
    
    except Exception as e:
        return Response({'detail': f'Transformation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)