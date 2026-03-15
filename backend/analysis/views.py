"""
Analysis Views - Refactored to use service classes
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from projects.models import Project
from .models import AnalysisRun, TransformationLog
from .statistics import StatisticalAnalyzer
from .services import AutomatedAnalysisService, DataLoaderService, TransformationService, ColumnActionService
from django.utils import timezone


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def automate_project(request, project_id):
    """Run the full automated profiling-to-summary pipeline for a project."""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    if not project.file_path:
        return Response({'detail': 'No data uploaded'}, status=status.HTTP_400_BAD_REQUEST)

    df = DataLoaderService.load_dataframe(project)
    if df is None:
        return Response({'detail': 'Failed to load data file'}, status=status.HTTP_400_BAD_REQUEST)

    auto_apply_cleaning = request.data.get('auto_apply_cleaning', True)
    if isinstance(auto_apply_cleaning, str):
        auto_apply_cleaning = auto_apply_cleaning.strip().lower() not in {'0', 'false', 'no', 'off'}

    try:
        result = AutomatedAnalysisService.run(
            project,
            df,
            actor=request.user,
            auto_apply_cleaning=auto_apply_cleaning,
            source='manual',
        )
        return Response({
            'message': 'Automated analysis pipeline completed successfully',
            'statistics': result['statistics'],
            'recommendations': result['recommendations'],
            'automation': result['automation'],
        })
    except Exception as e:
        return Response({'detail': f'Automation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        df = DataLoaderService.load_dataframe(project)
        if df is None:
            return Response({'detail': 'Failed to load data file'}, status=status.HTTP_400_BAD_REQUEST)
        
        from .insights import generate_cleaning_recommendations_without_ai
        recommendations = generate_cleaning_recommendations_without_ai(df)
        
        AnalysisRun.objects.create(
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
    """Apply transformation rules to project data"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    rules = request.data.get('rules', [])
    if not rules:
        return Response({'detail': 'No transformation rules provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        df = DataLoaderService.load_dataframe(project)
        if df is None:
            return Response({'detail': 'Failed to load data file'}, status=status.HTTP_400_BAD_REQUEST)
        
        original_shape = df.shape
        df, applied = TransformationService.apply_rules(df, rules, project)
        processed_result = TransformationService.save_processed_data(df, project.project_id)
        # save_processed_data returns (processed_path, backup_path)
        if isinstance(processed_result, (list, tuple)):
            processed_path, backup_path = processed_result
        else:
            processed_path = processed_result
            backup_path = None

        project.processed_file_path = processed_path
        project.status = 'transformed'
        # Audit the applied transformations
        entry = {
            'timestamp': timezone.now().isoformat(),
            'user': getattr(request.user, 'email', str(request.user.id)),
            'actions': applied,
            'backup_path': backup_path,
            'original_shape': list(original_shape),
            'new_shape': list(df.shape)
        }
        existing = project.applied_transformations or []
        existing.append(entry)
        project.applied_transformations = existing
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
    """Get comprehensive descriptive statistics"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = DataLoaderService.load_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        analyzer = StatisticalAnalyzer(df)
        return Response(analyzer.get_descriptive_statistics())
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
    
    df = DataLoaderService.load_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    method = request.query_params.get('method', 'pearson')
    
    try:
        analyzer = StatisticalAnalyzer(df)
        return Response(analyzer.get_correlation_matrix(method=method))
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
    
    df = DataLoaderService.load_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    column = request.query_params.get('column')
    bins = int(request.query_params.get('bins', 20))
    
    try:
        analyzer = StatisticalAnalyzer(df)
        return Response(analyzer.get_distribution_analysis(column=column, bins=bins))
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
    
    df = DataLoaderService.load_dataframe(project)
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
    
    df = DataLoaderService.load_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    column = request.query_params.get('column')
    if not column:
        return Response({'detail': 'Column parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        analyzer = StatisticalAnalyzer(df)
        return Response(analyzer.get_column_analysis(column))
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
    
    df = DataLoaderService.load_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    columns = DataLoaderService.get_columns_info(df)
    column_types = DataLoaderService.get_column_types(df)
    
    return Response({
        'columns': columns,
        **column_types
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quick_insights(request, project_id):
    """Generate rule-based quick insights - NO AI REQUIRED"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = DataLoaderService.load_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from .insights import generate_insights_without_ai
        
        analyzer = StatisticalAnalyzer(df)
        statistics = analyzer.get_descriptive_statistics()
        correlation = analyzer.get_correlation_matrix()
        
        return Response(generate_insights_without_ai(statistics, correlation))
    except Exception as e:
        return Response({'detail': f'Insights generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_column_actions(request, project_id):
    """Get recommended actions for columns"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = DataLoaderService.load_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    column = request.query_params.get('column')
    
    try:
        from .insights import InsightsGenerator, get_all_column_actions
        
        analyzer = StatisticalAnalyzer(df)
        statistics = analyzer.get_descriptive_statistics()
        
        if column:
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
            return Response(generator.generate_column_actions(column, col_stats, col_type))
        else:
            return Response({'columns': get_all_column_actions(statistics)})
    
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
    
    df = DataLoaderService.load_dataframe(project)
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
        
        # Apply the action
        df, changes_made = ColumnActionService.apply_action(
            df, project, column, action, strategy, value
        )
        
        # Save and log
        processed_path = ColumnActionService.save_and_log(
            df, project, column, action, strategy, changes_made
        )
        
        project.processed_file_path = processed_path
        project.status = 'transformed'
        project.save()
        
        return Response({
            'message': 'Action applied successfully',
            'changes': changes_made,
            'original_shape': original_shape,
            'new_shape': df.shape
        })
    
    except Exception as e:
        return Response({'detail': f'Action failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rollback_transformations(request, project_id):
    """Rollback transformations for a project using the latest backup entry."""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    applied = project.applied_transformations or []
    if not applied:
        return Response({'detail': 'No applied transformations to rollback'}, status=status.HTTP_400_BAD_REQUEST)

    last_entry = applied[-1]
    backup_path = last_entry.get('backup_path')
    if not backup_path:
        return Response({'detail': 'No backup available for the last transformation'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        restored = TransformationService.restore_backup(project.project_id, backup_path)
        # Add audit entry
        audit = {
            'timestamp': timezone.now().isoformat(),
            'user': getattr(request.user, 'email', str(request.user.id)),
            'action': 'rollback',
            'restored_from': backup_path,
            'restored_to': restored
        }
        existing = project.applied_transformations or []
        existing.append(audit)
        project.applied_transformations = existing
        project.save()

        return Response({'message': 'Rollback completed', 'restored_path': restored})
    except Exception as e:
        return Response({'detail': f'Rollback failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
