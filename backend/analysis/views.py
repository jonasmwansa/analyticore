from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import pandas as pd
import numpy as np
import os
from projects.models import Project
from .models import AnalysisRun, TransformationLog
from .statistics import StatisticalAnalyzer


def load_project_dataframe(project):
    """Helper to load project data into a DataFrame"""
    file_path = project.processed_file_path or project.file_path
    
    if not file_path or not os.path.exists(file_path):
        return None
    
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file_path)
    elif file_path.endswith('.json'):
        return pd.read_json(file_path)
    return None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_data(request, project_id):
    """Generate rule-based cleaning recommendations - NO AI REQUIRED"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not project.file_path:
        return Response({'detail': 'No data uploaded'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        df = load_project_dataframe(project)
        if df is None:
            return Response({'detail': 'Failed to load data file'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use rule-based recommendations (NO AI)
        from .insights import generate_cleaning_recommendations_without_ai
        recommendations = generate_cleaning_recommendations_without_ai(df)
        
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
        df = load_project_dataframe(project)
        if df is None:
            return Response({'detail': 'Failed to load data file'}, status=status.HTTP_400_BAD_REQUEST)
        
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_statistics(request, project_id):
    """Get comprehensive descriptive statistics for the project data"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        analyzer = StatisticalAnalyzer(df)
        statistics = analyzer.get_descriptive_statistics()
        return Response(statistics)
    except Exception as e:
        return Response({'detail': f'Statistics calculation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_correlation(request, project_id):
    """Get correlation matrix for numeric columns"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    method = request.query_params.get('method', 'pearson')
    
    try:
        analyzer = StatisticalAnalyzer(df)
        correlation = analyzer.get_correlation_matrix(method=method)
        return Response(correlation)
    except Exception as e:
        return Response({'detail': f'Correlation calculation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_distribution(request, project_id):
    """Get distribution analysis for numeric columns"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    column = request.query_params.get('column')
    bins = int(request.query_params.get('bins', 20))
    
    try:
        analyzer = StatisticalAnalyzer(df)
        distribution = analyzer.get_distribution_analysis(column=column, bins=bins)
        return Response(distribution)
    except Exception as e:
        return Response({'detail': f'Distribution analysis failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chart_data(request, project_id):
    """Get data formatted for specific chart types"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    chart_type = request.query_params.get('type', 'scatter')
    x_column = request.query_params.get('x')
    y_column = request.query_params.get('y')
    color_by = request.query_params.get('color')
    limit = int(request.query_params.get('limit', 1000))
    
    try:
        analyzer = StatisticalAnalyzer(df)
        chart_data = analyzer.get_chart_data(
            chart_type=chart_type,
            x_column=x_column,
            y_column=y_column,
            color_by=color_by,
            limit=limit
        )
        return Response(chart_data)
    except Exception as e:
        return Response({'detail': f'Chart data generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_column_info(request, project_id):
    """Get detailed analysis of a specific column"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    column = request.query_params.get('column')
    if not column:
        return Response({'detail': 'Column parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        analyzer = StatisticalAnalyzer(df)
        column_info = analyzer.get_column_analysis(column)
        return Response(column_info)
    except Exception as e:
        return Response({'detail': f'Column analysis failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_columns(request, project_id):
    """Get list of columns with their types"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    import numpy as np
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    columns = []
    for col in df.columns:
        col_type = 'numeric' if col in numeric_cols else ('datetime' if col in datetime_cols else 'categorical')
        columns.append({
            'name': col,
            'type': col_type,
            'dtype': str(df[col].dtype)
        })
    
    return Response({
        'columns': columns,
        'numeric': numeric_cols,
        'categorical': categorical_cols,
        'datetime': datetime_cols
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quick_insights(request, project_id):
    """Generate rule-based quick insights summary for the project data - NO AI REQUIRED"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from .insights import generate_insights_without_ai
        from .statistics import StatisticalAnalyzer
        
        # Get statistics first
        analyzer = StatisticalAnalyzer(df)
        statistics = analyzer.get_descriptive_statistics()
        correlation = analyzer.get_correlation_matrix()
        
        # Generate insights using rule-based logic (NO AI)
        insights = generate_insights_without_ai(statistics, correlation)
        
        return Response(insights)
    except Exception as e:
        return Response({'detail': f'Insights generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_column_actions(request, project_id):
    """Get recommended actions for all columns or a specific column"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    column = request.query_params.get('column')
    
    try:
        from .insights import InsightsGenerator, get_all_column_actions
        from .statistics import StatisticalAnalyzer
        
        analyzer = StatisticalAnalyzer(df)
        statistics = analyzer.get_descriptive_statistics()
        
        if column:
            # Get actions for a specific column
            col_type = None
            col_stats = None
            
            if column in statistics.get('numeric', {}):
                col_type = 'numeric'
                col_stats = statistics['numeric'][column]
            elif column in statistics.get('categorical', {}):
                col_type = 'categorical'
                col_stats = statistics['categorical'][column]
            elif column in statistics.get('datetime', {}):
                col_type = 'datetime'
                col_stats = statistics['datetime'][column]
            
            if not col_stats:
                return Response({'detail': f'Column {column} not found'}, status=status.HTTP_404_NOT_FOUND)
            
            generator = InsightsGenerator(str(project_id))
            actions = generator.generate_column_actions(column, col_stats, col_type)
            return Response(actions)
        else:
            # Get actions for all columns
            all_actions = get_all_column_actions(statistics)
            return Response({'columns': all_actions})
    
    except Exception as e:
        return Response({'detail': f'Action generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_column_action(request, project_id):
    """Apply a specific action to a column"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    column = request.data.get('column')
    action = request.data.get('action')
    strategy = request.data.get('strategy')
    value = request.data.get('value')
    
    if not column or not action:
        return Response({'detail': 'Column and action are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if column not in df.columns:
        return Response({'detail': f'Column {column} not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        original_shape = df.shape
        changes_made = []
        
        if action == 'fill_missing':
            null_count_before = df[column].isnull().sum()
            
            if strategy == 'mean':
                df[column].fillna(df[column].mean(), inplace=True)
            elif strategy == 'median':
                df[column].fillna(df[column].median(), inplace=True)
            elif strategy == 'mode':
                mode_val = df[column].mode()
                if len(mode_val) > 0:
                    df[column].fillna(mode_val[0], inplace=True)
            elif strategy == 'forward_fill':
                df[column].fillna(method='ffill', inplace=True)
            elif strategy == 'backward_fill':
                df[column].fillna(method='bfill', inplace=True)
            elif strategy == 'constant' and value is not None:
                df[column].fillna(value, inplace=True)
            
            null_count_after = df[column].isnull().sum()
            changes_made.append(f"Filled {null_count_before - null_count_after} missing values using {strategy}")
        
        elif action == 'drop_rows':
            rows_before = len(df)
            df.dropna(subset=[column], inplace=True)
            rows_after = len(df)
            changes_made.append(f"Dropped {rows_before - rows_after} rows with missing values")
        
        elif action == 'remove_outliers':
            if strategy == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                rows_before = len(df)
                df = df[(df[column] >= lower) & (df[column] <= upper)]
                rows_after = len(df)
                changes_made.append(f"Removed {rows_before - rows_after} outliers using IQR method")
        
        elif action == 'cap_outliers':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            capped_low = (df[column] < lower).sum()
            capped_high = (df[column] > upper).sum()
            df[column] = df[column].clip(lower=lower, upper=upper)
            changes_made.append(f"Capped {capped_low} low values and {capped_high} high values")
        
        elif action == 'convert_type':
            target_type = strategy or request.data.get('target_type')
            if target_type == 'numeric':
                df[column] = pd.to_numeric(df[column], errors='coerce')
                changes_made.append(f"Converted {column} to numeric type")
            elif target_type == 'datetime':
                df[column] = pd.to_datetime(df[column], errors='coerce')
                changes_made.append(f"Converted {column} to datetime type")
            elif target_type == 'string':
                df[column] = df[column].astype(str)
                changes_made.append(f"Converted {column} to string type")
            elif target_type == 'category':
                df[column] = df[column].astype('category')
                changes_made.append(f"Converted {column} to category type")
        
        elif action == 'text_transform':
            if strategy == 'trim':
                df[column] = df[column].astype(str).str.strip()
                changes_made.append(f"Trimmed whitespace from {column}")
            elif strategy == 'lowercase':
                df[column] = df[column].astype(str).str.lower()
                changes_made.append(f"Converted {column} to lowercase")
            elif strategy == 'uppercase':
                df[column] = df[column].astype(str).str.upper()
                changes_made.append(f"Converted {column} to uppercase")
            elif strategy == 'remove_special':
                df[column] = df[column].astype(str).str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
                changes_made.append(f"Removed special characters from {column}")
        
        elif action == 'remove_duplicates':
            rows_before = len(df)
            if column:
                df.drop_duplicates(subset=[column], keep='first', inplace=True)
            else:
                df.drop_duplicates(keep='first', inplace=True)
            rows_after = len(df)
            changes_made.append(f"Removed {rows_before - rows_after} duplicate rows")
        
        # Save processed data
        processed_path = os.path.join(
            settings.PIPELINE_STORAGE_PATH,
            'processed',
            f"{project_id}_processed.csv"
        )
        df.to_csv(processed_path, index=False)
        
        project.processed_file_path = processed_path
        project.status = 'transformed'
        project.save()
        
        # Log the transformation
        TransformationLog.objects.create(
            project=project,
            step_name='Column Action',
            action=action,
            target=column,
            reason=f"User applied {action} with {strategy or 'default'} strategy",
            impact={'changes': changes_made},
            confidence=1.0
        )
        
        return Response({
            'message': 'Action applied successfully',
            'changes': changes_made,
            'original_shape': original_shape,
            'new_shape': df.shape
        })
    
    except Exception as e:
        return Response({'detail': f'Action failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

