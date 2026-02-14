"""
Magic Analysis Views - One-Click Data Analysis API Endpoints
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from projects.models import Project
from .services import DataLoaderService, TransformationService
from .magic_analysis_service import run_magic_analysis


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def run_magic_analysis_view(request, project_id):
    """
    One-click magic analysis endpoint
    Returns comprehensive analysis with plain-English insights
    """
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not project.file_path:
        return Response({'detail': 'No data uploaded'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        df = DataLoaderService.load_dataframe(project)
        if df is None:
            return Response({'detail': 'Failed to load data file'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Run magic analysis
        result = run_magic_analysis(df, project.name)
        
        return Response(result)
    
    except Exception as e:
        return Response(
            {'detail': f'Magic analysis failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Alias for backwards compatibility
run_magic_analysis = run_magic_analysis_view


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_magic_cleaning(request, project_id):
    """
    Apply selected cleaning operations from magic analysis suggestions
    """
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not project.file_path:
        return Response({'detail': 'No data uploaded'}, status=status.HTTP_400_BAD_REQUEST)
    
    cleaning_actions = request.data.get('actions', [])
    if not cleaning_actions:
        return Response({'detail': 'No cleaning actions provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        df = DataLoaderService.load_dataframe(project)
        if df is None:
            return Response({'detail': 'Failed to load data file'}, status=status.HTTP_400_BAD_REQUEST)
        
        original_shape = df.shape
        changes_log = []
        
        for action in cleaning_actions:
            column = action.get('column')
            issue = action.get('issue')
            strategy = action.get('strategy')
            value = action.get('value')  # For constant fill
            
            if issue == 'missing_values':
                df, change = _handle_missing_values(df, column, strategy, value)
                changes_log.append(change)
            
            elif issue == 'duplicates':
                df, change = _handle_duplicates(df, strategy)
                changes_log.append(change)
            
            elif issue == 'type_conversion':
                df, change = _handle_type_conversion(df, column, strategy)
                changes_log.append(change)
            
            elif issue == 'text_normalization':
                df, change = _handle_text_normalization(df, column, strategy)
                changes_log.append(change)
            
            elif issue == 'outliers':
                df, change = _handle_outliers(df, column, strategy)
                changes_log.append(change)
        
        # Save the cleaned data
        processed_path = TransformationService.save_processed_data(df, project.project_id)
        
        project.processed_file_path = processed_path
        project.status = 'transformed'
        project.save()
        
        return Response({
            'message': 'Cleaning operations applied successfully',
            'original_shape': original_shape,
            'new_shape': df.shape,
            'changes': changes_log,
            'rows_affected': original_shape[0] - df.shape[0] if original_shape[0] != df.shape[0] else 0
        })
    
    except Exception as e:
        return Response(
            {'detail': f'Cleaning failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _handle_missing_values(df, column, strategy, value=None):
    """Handle missing values with the specified strategy"""
    import pandas as pd
    import numpy as np
    
    if column not in df.columns:
        return df, {'column': column, 'status': 'error', 'message': 'Column not found'}
    
    original_missing = df[column].isnull().sum()
    
    if strategy == 'mean':
        fill_value = df[column].mean()
        df[column] = df[column].fillna(fill_value)
        
    elif strategy == 'median':
        fill_value = df[column].median()
        df[column] = df[column].fillna(fill_value)
        
    elif strategy == 'mode':
        fill_value = df[column].mode()[0] if len(df[column].mode()) > 0 else None
        if fill_value is not None:
            df[column] = df[column].fillna(fill_value)
            
    elif strategy == 'forward_fill':
        df[column] = df[column].fillna(method='ffill')
        
    elif strategy == 'backward_fill':
        df[column] = df[column].fillna(method='bfill')
        
    elif strategy == 'constant':
        fill_value = value if value is not None else 0
        df[column] = df[column].fillna(fill_value)
        
    elif strategy == 'drop_rows':
        df = df.dropna(subset=[column])
    
    new_missing = df[column].isnull().sum() if column in df.columns else 0
    
    return df, {
        'column': column,
        'status': 'success',
        'strategy': strategy,
        'values_filled': int(original_missing - new_missing)
    }


def _handle_duplicates(df, strategy):
    """Handle duplicate rows"""
    original_count = len(df)
    
    if strategy == 'remove_duplicates':
        df = df.drop_duplicates()
    elif strategy == 'keep_first':
        df = df.drop_duplicates(keep='first')
    elif strategy == 'keep_last':
        df = df.drop_duplicates(keep='last')
    
    removed = original_count - len(df)
    
    return df, {
        'column': '__all__',
        'status': 'success',
        'strategy': strategy,
        'rows_removed': removed
    }


def _handle_type_conversion(df, column, strategy):
    """Handle data type conversion"""
    import pandas as pd
    
    if column not in df.columns:
        return df, {'column': column, 'status': 'error', 'message': 'Column not found'}
    
    original_dtype = str(df[column].dtype)
    
    if strategy == 'to_numeric':
        df[column] = pd.to_numeric(df[column], errors='coerce')
    elif strategy == 'to_datetime':
        df[column] = pd.to_datetime(df[column], errors='coerce')
    elif strategy == 'to_string':
        df[column] = df[column].astype(str)
    elif strategy == 'to_category':
        df[column] = df[column].astype('category')
    
    new_dtype = str(df[column].dtype)
    
    return df, {
        'column': column,
        'status': 'success',
        'strategy': strategy,
        'original_dtype': original_dtype,
        'new_dtype': new_dtype
    }


def _handle_text_normalization(df, column, strategy):
    """Handle text normalization"""
    import re
    
    if column not in df.columns:
        return df, {'column': column, 'status': 'error', 'message': 'Column not found'}
    
    if strategy == 'trim':
        df[column] = df[column].astype(str).str.strip()
    elif strategy == 'lowercase':
        df[column] = df[column].astype(str).str.lower()
    elif strategy == 'uppercase':
        df[column] = df[column].astype(str).str.upper()
    elif strategy == 'remove_special':
        df[column] = df[column].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', x))
    
    return df, {
        'column': column,
        'status': 'success',
        'strategy': strategy
    }


def _handle_outliers(df, column, strategy):
    """Handle outliers using IQR method"""
    import numpy as np
    
    if column not in df.columns:
        return df, {'column': column, 'status': 'error', 'message': 'Column not found'}
    
    col_data = df[column].dropna()
    q1 = col_data.quantile(0.25)
    q3 = col_data.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    original_count = len(df)
    
    if strategy == 'remove':
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    elif strategy == 'cap':
        df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
    
    return df, {
        'column': column,
        'status': 'success',
        'strategy': strategy,
        'lower_bound': round(float(lower_bound), 4),
        'upper_bound': round(float(upper_bound), 4),
        'rows_affected': original_count - len(df) if strategy == 'remove' else 0
    }
