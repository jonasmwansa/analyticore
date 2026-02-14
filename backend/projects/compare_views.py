"""
Compare Projects Views - Compare statistics across multiple projects
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import pandas as pd
import numpy as np

from projects.models import Project
from analysis.services import DataLoaderService
from analysis.statistics import StatisticalAnalyzer
from analysis.magic_analysis_service import run_magic_analysis


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def compare_projects(request):
    """
    Compare multiple projects (2-4 projects)
    Returns side-by-side comparison of statistics and quality scores
    """
    project_ids = request.data.get('project_ids', [])
    
    if len(project_ids) < 2:
        return Response({'detail': 'At least 2 projects required for comparison'}, status=status.HTTP_400_BAD_REQUEST)
    
    if len(project_ids) > 4:
        return Response({'detail': 'Maximum 4 projects can be compared at once'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        comparisons = []
        
        for project_id in project_ids:
            try:
                project = Project.objects.get(project_id=project_id, user=request.user)
            except Project.DoesNotExist:
                return Response({'detail': f'Project {project_id} not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if not project.file_path:
                return Response({'detail': f'Project "{project.name}" has no data'}, status=status.HTTP_400_BAD_REQUEST)
            
            df = DataLoaderService.load_dataframe(project)
            if df is None:
                return Response({'detail': f'Failed to load data for "{project.name}"'}, status=status.HTTP_400_BAD_REQUEST)
            
            analyzer = StatisticalAnalyzer(df)
            stats = analyzer.get_descriptive_statistics()
            
            # Run magic analysis for quality score
            magic_result = run_magic_analysis(df, project.name)
            
            # Calculate column type breakdown
            numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
            categorical_cols = len(df.select_dtypes(include=['object', 'category']).columns)
            datetime_cols = len(df.select_dtypes(include=['datetime64']).columns)
            
            comparison_data = {
                'project_id': str(project.project_id),
                'project_name': project.name,
                'created_at': project.created_at.isoformat() if project.created_at else None,
                
                # Basic stats
                'total_rows': stats['summary']['total_rows'],
                'total_columns': stats['summary']['total_columns'],
                
                # Column types
                'numeric_columns': numeric_cols,
                'categorical_columns': categorical_cols,
                'datetime_columns': datetime_cols,
                
                # Data quality
                'missing_values': stats['summary']['total_missing'],
                'missing_percentage': round(stats['summary']['total_missing'] / (stats['summary']['total_rows'] * stats['summary']['total_columns']) * 100, 2) if stats['summary']['total_rows'] > 0 else 0,
                'duplicate_rows': stats['summary']['total_duplicates'],
                'duplicate_percentage': round(stats['summary']['total_duplicates'] / stats['summary']['total_rows'] * 100, 2) if stats['summary']['total_rows'] > 0 else 0,
                
                # Quality score from magic analysis
                'quality_score': magic_result['executive_summary']['quality_score'],
                'quality_label': magic_result['executive_summary']['quality_label'],
                
                # Issues summary
                'issues_count': len(magic_result.get('data_quality', {}).get('issues', [])),
                'critical_issues': len([i for i in magic_result.get('data_quality', {}).get('issues', []) if i.get('severity') == 'critical']),
                'warning_issues': len([i for i in magic_result.get('data_quality', {}).get('issues', []) if i.get('severity') == 'warning']),
                
                # Column details for radar chart
                'completeness': round(100 - (stats['summary']['total_missing'] / (stats['summary']['total_rows'] * stats['summary']['total_columns']) * 100), 1) if stats['summary']['total_rows'] > 0 else 100,
                'uniqueness': round(100 - (stats['summary']['total_duplicates'] / stats['summary']['total_rows'] * 100), 1) if stats['summary']['total_rows'] > 0 else 100,
                'consistency': magic_result['executive_summary']['quality_score'],  # Use quality score as proxy
                
                # Numeric column statistics summary
                'numeric_stats': _get_numeric_summary(stats['numeric']) if stats['numeric'] else None,
            }
            
            comparisons.append(comparison_data)
        
        # Calculate comparison metrics
        comparison_result = {
            'projects': comparisons,
            'comparison_metrics': _calculate_comparison_metrics(comparisons),
            'radar_data': _prepare_radar_data(comparisons),
            'bar_chart_data': _prepare_bar_chart_data(comparisons),
        }
        
        return Response(comparison_result)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'detail': f'Comparison failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_numeric_summary(numeric_stats):
    """Get summary statistics for numeric columns"""
    if not numeric_stats:
        return None
    
    means = [v['mean'] for v in numeric_stats.values() if v['mean'] is not None]
    stds = [v['std'] for v in numeric_stats.values() if v['std'] is not None]
    missing_pcts = [v['missing_pct'] for v in numeric_stats.values()]
    
    return {
        'avg_mean': round(np.mean(means), 4) if means else None,
        'avg_std': round(np.mean(stds), 4) if stds else None,
        'avg_missing_pct': round(np.mean(missing_pcts), 2) if missing_pcts else 0,
        'columns_with_missing': len([p for p in missing_pcts if p > 0]),
    }


def _calculate_comparison_metrics(comparisons):
    """Calculate comparison metrics between projects"""
    if len(comparisons) < 2:
        return {}
    
    metrics = {
        'best_quality': max(comparisons, key=lambda x: x['quality_score'])['project_name'],
        'most_rows': max(comparisons, key=lambda x: x['total_rows'])['project_name'],
        'most_columns': max(comparisons, key=lambda x: x['total_columns'])['project_name'],
        'fewest_issues': min(comparisons, key=lambda x: x['issues_count'])['project_name'],
        'most_complete': max(comparisons, key=lambda x: x['completeness'])['project_name'],
        
        'avg_quality_score': round(np.mean([c['quality_score'] for c in comparisons]), 1),
        'avg_rows': int(np.mean([c['total_rows'] for c in comparisons])),
        'avg_columns': int(np.mean([c['total_columns'] for c in comparisons])),
        'total_issues': sum(c['issues_count'] for c in comparisons),
    }
    
    return metrics


def _prepare_radar_data(comparisons):
    """Prepare data for radar chart visualization"""
    radar_data = []
    
    metrics = ['completeness', 'uniqueness', 'consistency', 'quality_score']
    
    for metric in metrics:
        entry = {'metric': metric.replace('_', ' ').title()}
        for comp in comparisons:
            entry[comp['project_name']] = comp.get(metric, 0)
        radar_data.append(entry)
    
    return radar_data


def _prepare_bar_chart_data(comparisons):
    """Prepare data for bar chart comparisons"""
    return {
        'rows': [{'name': c['project_name'], 'value': c['total_rows']} for c in comparisons],
        'columns': [{'name': c['project_name'], 'value': c['total_columns']} for c in comparisons],
        'quality': [{'name': c['project_name'], 'value': c['quality_score']} for c in comparisons],
        'missing': [{'name': c['project_name'], 'value': c['missing_percentage']} for c in comparisons],
        'issues': [{'name': c['project_name'], 'value': c['issues_count']} for c in comparisons],
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comparable_projects(request):
    """
    Get list of projects that can be compared (have data uploaded)
    """
    try:
        projects = Project.objects.filter(user=request.user, file_path__isnull=False).exclude(file_path='')
        
        project_list = []
        for project in projects:
            project_list.append({
                'project_id': str(project.project_id),
                'name': project.name,
                'created_at': project.created_at.isoformat() if project.created_at else None,
                'status': project.status,
                'row_count': project.statistics.get('total_rows') if project.statistics else None,
            })
        
        return Response({'projects': project_list})
    
    except Exception as e:
        return Response({'detail': f'Failed to fetch projects: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
