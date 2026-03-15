"""
Enhanced Export Views - Export statistics, correlations, distributions, and visualizations
"""
import io
import base64
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from projects.models import Project
from analysis.services import DataLoaderService
from analysis.statistics import StatisticalAnalyzer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_summary_statistics(request, project_id):
    """
    Export summary statistics in CSV or Excel format
    """
    export_format = request.query_params.get('export_format', 'csv')
    
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
        
        analyzer = StatisticalAnalyzer(df)
        stats = analyzer.get_descriptive_statistics()
        safe_name = project.name.replace(' ', '_').replace('"', '').replace("'", '')
        
        if export_format == 'csv':
            # Create CSV content
            lines = []
            lines.append('SUMMARY STATISTICS')
            lines.append(f'Project,{project.name}')
            lines.append(f'Total Rows,{stats["summary"]["total_rows"]}')
            lines.append(f'Total Columns,{stats["summary"]["total_columns"]}')
            lines.append(f'Numeric Columns,{stats["summary"]["numeric_columns"]}')
            lines.append(f'Categorical Columns,{stats["summary"]["categorical_columns"]}')
            lines.append(f'Total Missing,{stats["summary"]["total_missing"]}')
            lines.append(f'Total Duplicates,{stats["summary"]["total_duplicates"]}')
            lines.append('')
            
            # Numeric columns
            if stats['numeric']:
                lines.append('NUMERIC COLUMNS')
                lines.append('Column,Count,Mean,Std,Min,25%,Median,75%,Max,Skewness,Kurtosis,Missing,Missing %')
                for col, data in stats['numeric'].items():
                    lines.append(f'{col},{data["count"]},{data["mean"]},{data["std"]},{data["min"]},{data["25%"]},{data["50%"]},{data["75%"]},{data["max"]},{data["skewness"]},{data["kurtosis"]},{data["missing"]},{data["missing_pct"]}')
                lines.append('')
            
            # Categorical columns
            if stats['categorical']:
                lines.append('CATEGORICAL COLUMNS')
                lines.append('Column,Count,Unique,Top Value,Frequency,Missing,Missing %')
                for col, data in stats['categorical'].items():
                    lines.append(f'{col},{data["count"]},{data["unique"]},{data["top"]},{data["freq"]},{data["missing"]},{data["missing_pct"]}')
            
            csv_content = '\n'.join(lines)
            return Response({
                'filename': f'{safe_name}_summary_statistics.csv',
                'content_type': 'text/csv',
                'content': csv_content
            })
        
        elif export_format == 'excel':
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Summary sheet
                summary_df = pd.DataFrame([stats['summary']]).T
                summary_df.columns = ['Value']
                summary_df.index.name = 'Metric'
                summary_df.to_excel(writer, sheet_name='Summary')
                
                # Numeric statistics
                if stats['numeric']:
                    numeric_df = pd.DataFrame(stats['numeric']).T
                    numeric_df.index.name = 'Column'
                    numeric_df.to_excel(writer, sheet_name='Numeric Statistics')
                
                # Categorical statistics
                if stats['categorical']:
                    cat_data = []
                    for col, data in stats['categorical'].items():
                        cat_data.append({
                            'column': col,
                            'count': data['count'],
                            'unique': data['unique'],
                            'top': data['top'],
                            'freq': data['freq'],
                            'missing': data['missing'],
                            'missing_pct': data['missing_pct']
                        })
                    pd.DataFrame(cat_data).to_excel(writer, sheet_name='Categorical Statistics', index=False)
            
            output.seek(0)
            excel_base64 = base64.b64encode(output.read()).decode('utf-8')
            
            return Response({
                'filename': f'{safe_name}_summary_statistics.xlsx',
                'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'content': excel_base64,
                'encoding': 'base64'
            })
        
        return Response({'detail': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({'detail': f'Export failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_correlation_matrix(request, project_id):
    """
    Export correlation matrix in CSV or Excel format
    """
    export_format = request.query_params.get('export_format', 'csv')
    method = request.query_params.get('method', 'pearson')  # pearson, spearman, kendall
    
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
        
        analyzer = StatisticalAnalyzer(df)
        corr_data = analyzer.get_correlation_matrix(method=method)
        safe_name = project.name.replace(' ', '_').replace('"', '').replace("'", '')
        
        if not corr_data['columns']:
            return Response({'detail': 'Not enough numeric columns for correlation'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Build correlation DataFrame
        corr_df = pd.DataFrame(corr_data['matrix'])
        
        if export_format == 'csv':
            output = io.StringIO()
            output.write(f'# Correlation Matrix ({method.capitalize()} method)\n')
            output.write(f'# Project: {project.name}\n\n')
            corr_df.to_csv(output)
            output.write('\n# Top Correlations\n')
            output.write('Column 1,Column 2,Correlation,Strength\n')
            for item in corr_data['top_correlations']:
                output.write(f'{item["column1"]},{item["column2"]},{item["correlation"]},{item["strength"]}\n')
            
            return Response({
                'filename': f'{safe_name}_correlation_{method}.csv',
                'content_type': 'text/csv',
                'content': output.getvalue()
            })
        
        elif export_format == 'excel':
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Correlation matrix
                corr_df.to_excel(writer, sheet_name='Correlation Matrix')
                
                # Top correlations
                if corr_data['top_correlations']:
                    top_df = pd.DataFrame(corr_data['top_correlations'])
                    top_df.to_excel(writer, sheet_name='Top Correlations', index=False)
                
                # Metadata
                meta_df = pd.DataFrame([{
                    'Project': project.name,
                    'Method': method,
                    'Numeric Columns': len(corr_data['columns'])
                }])
                meta_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            output.seek(0)
            excel_base64 = base64.b64encode(output.read()).decode('utf-8')
            
            return Response({
                'filename': f'{safe_name}_correlation_{method}.xlsx',
                'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'content': excel_base64,
                'encoding': 'base64'
            })
        
        return Response({'detail': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({'detail': f'Export failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_distribution_analysis(request, project_id):
    """
    Export distribution analysis in CSV or Excel format
    """
    export_format = request.query_params.get('export_format', 'csv')
    column = request.query_params.get('column')  # Optional: specific column
    bins = int(request.query_params.get('bins', 20))
    
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
        
        analyzer = StatisticalAnalyzer(df)
        dist_data = analyzer.get_distribution_analysis(column=column, bins=bins)
        safe_name = project.name.replace(' ', '_').replace('"', '').replace("'", '')
        
        if export_format == 'csv':
            lines = []
            lines.append('# Distribution Analysis')
            lines.append(f'# Project: {project.name}')
            lines.append('')
            
            for col_name, data in dist_data['distributions'].items():
                if 'message' in data:
                    continue
                    
                lines.append(f'## {col_name}')
                lines.append(f'Distribution Type: {data["distribution_type"]}')
                lines.append(f'Skewness: {data["skewness"]}')
                lines.append(f'Kurtosis: {data["kurtosis"]}')
                lines.append(f'Is Symmetric: {data["is_symmetric"]}')
                lines.append('')
                
                # Box plot stats
                bp = data['box_plot']
                lines.append('Box Plot Statistics:')
                lines.append('Min,Q1,Median,Q3,Max,IQR,Outliers Count')
                lines.append(f'{bp["min"]},{bp["q1"]},{bp["median"]},{bp["q3"]},{bp["max"]},{bp["iqr"]},{bp["outliers_count"]}')
                lines.append('')
                
                # Normality tests
                if data['normality_tests']:
                    lines.append('Normality Tests:')
                    lines.append('Test,Statistic,P-Value,Is Normal')
                    for test_name, test_data in data['normality_tests'].items():
                        lines.append(f'{test_name},{test_data["statistic"]},{test_data["p_value"]},{test_data["is_normal"]}')
                    lines.append('')
                
                # Histogram data
                lines.append('Histogram:')
                lines.append('Bin Start,Bin End,Count')
                for bin_data in data['histogram']:
                    lines.append(f'{bin_data["bin_start"]},{bin_data["bin_end"]},{bin_data["count"]}')
                lines.append('')
            
            return Response({
                'filename': f'{safe_name}_distribution_analysis.csv',
                'content_type': 'text/csv',
                'content': '\n'.join(lines)
            })
        
        elif export_format == 'excel':
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = []
                for col_name, data in dist_data['distributions'].items():
                    if 'message' in data:
                        continue
                    summary_data.append({
                        'Column': col_name,
                        'Distribution Type': data['distribution_type'],
                        'Skewness': data['skewness'],
                        'Kurtosis': data['kurtosis'],
                        'Is Symmetric': data['is_symmetric'],
                        'Min': data['box_plot']['min'],
                        'Q1': data['box_plot']['q1'],
                        'Median': data['box_plot']['median'],
                        'Q3': data['box_plot']['q3'],
                        'Max': data['box_plot']['max'],
                        'IQR': data['box_plot']['iqr'],
                        'Outliers Count': data['box_plot']['outliers_count']
                    })
                if summary_data:
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Distribution Summary', index=False)
                
                # Histogram data for each column
                for col_name, data in dist_data['distributions'].items():
                    if 'message' in data or not data.get('histogram'):
                        continue
                    hist_df = pd.DataFrame(data['histogram'])
                    sheet_name = f'Hist_{col_name[:20]}'  # Truncate long names
                    hist_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Normality tests
                normality_data = []
                for col_name, data in dist_data['distributions'].items():
                    if 'message' in data:
                        continue
                    for test_name, test_data in data.get('normality_tests', {}).items():
                        normality_data.append({
                            'Column': col_name,
                            'Test': test_name,
                            'Statistic': test_data['statistic'],
                            'P-Value': test_data['p_value'],
                            'Is Normal': test_data['is_normal']
                        })
                if normality_data:
                    pd.DataFrame(normality_data).to_excel(writer, sheet_name='Normality Tests', index=False)
            
            output.seek(0)
            excel_base64 = base64.b64encode(output.read()).decode('utf-8')
            
            return Response({
                'filename': f'{safe_name}_distribution_analysis.xlsx',
                'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'content': excel_base64,
                'encoding': 'base64'
            })
        
        return Response({'detail': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({'detail': f'Export failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_visualization(request, project_id):
    """
    Export visualizations as PNG or SVG
    """
    export_format = request.query_params.get('export_format', 'png')  # png or svg
    chart_type = request.query_params.get('chart_type', 'correlation')  # correlation, distribution, summary
    column = request.query_params.get('column')  # For distribution charts
    
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
        
        safe_name = project.name.replace(' ', '_').replace('"', '').replace("'", '')
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Set style
        plt.style.use('seaborn-v0_8-whitegrid')
        
        if chart_type == 'correlation':
            if len(numeric_cols) < 2:
                return Response({'detail': 'Not enough numeric columns'}, status=status.HTTP_400_BAD_REQUEST)
            
            corr = df[numeric_cols].corr()
            fig, ax = plt.subplots(figsize=(12, 10))
            sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                       square=True, linewidths=0.5, ax=ax,
                       cbar_kws={'shrink': 0.8})
            ax.set_title(f'Correlation Matrix - {project.name}', fontsize=14, fontweight='bold')
            plt.tight_layout()
            filename = f'{safe_name}_correlation_heatmap'
        
        elif chart_type == 'distribution':
            target_col = column if column and column in numeric_cols else (numeric_cols[0] if numeric_cols else None)
            if not target_col:
                return Response({'detail': 'No numeric column available'}, status=status.HTTP_400_BAD_REQUEST)
            
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            
            # Histogram
            axes[0].hist(df[target_col].dropna(), bins=30, color='#6366F1', edgecolor='white', alpha=0.8)
            axes[0].set_xlabel(target_col)
            axes[0].set_ylabel('Frequency')
            axes[0].set_title(f'Distribution of {target_col}')
            
            # Box plot
            axes[1].boxplot(df[target_col].dropna(), vert=True, patch_artist=True,
                          boxprops=dict(facecolor='#6366F1', alpha=0.7))
            axes[1].set_ylabel(target_col)
            axes[1].set_title(f'Box Plot of {target_col}')
            
            fig.suptitle(f'{project.name} - {target_col} Distribution', fontsize=14, fontweight='bold')
            plt.tight_layout()
            filename = f'{safe_name}_{target_col}_distribution'
        
        elif chart_type == 'summary':
            # Create a summary dashboard with multiple charts
            fig = plt.figure(figsize=(16, 12))
            
            # 1. Missing values bar chart
            ax1 = fig.add_subplot(2, 2, 1)
            missing = df.isnull().sum()
            missing = missing[missing > 0].sort_values(ascending=True).tail(10)
            if len(missing) > 0:
                missing.plot(kind='barh', ax=ax1, color='#EF4444')
                ax1.set_title('Top 10 Columns with Missing Values')
                ax1.set_xlabel('Missing Count')
            else:
                ax1.text(0.5, 0.5, 'No Missing Values', ha='center', va='center', fontsize=14)
                ax1.set_title('Missing Values')
            
            # 2. Data type distribution
            ax2 = fig.add_subplot(2, 2, 2)
            dtype_counts = df.dtypes.astype(str).value_counts()
            colors = ['#6366F1', '#14B8A6', '#F59E0B', '#8B5CF6'][:len(dtype_counts)]
            ax2.pie(dtype_counts.values, labels=dtype_counts.index, autopct='%1.1f%%', colors=colors)
            ax2.set_title('Column Data Types')
            
            # 3. Numeric columns distribution summary (box plots)
            ax3 = fig.add_subplot(2, 2, 3)
            if len(numeric_cols) > 0:
                # Normalize for visualization
                numeric_df = df[numeric_cols[:8]].copy()
                numeric_df = (numeric_df - numeric_df.mean()) / numeric_df.std()
                numeric_df.boxplot(ax=ax3, vert=True, patch_artist=True)
                ax3.set_title('Numeric Columns (Standardized)')
                ax3.tick_params(axis='x', rotation=45)
            else:
                ax3.text(0.5, 0.5, 'No Numeric Columns', ha='center', va='center', fontsize=14)
            
            # 4. Row count info
            ax4 = fig.add_subplot(2, 2, 4)
            stats_text = f"""
            Total Rows: {len(df):,}
            Total Columns: {len(df.columns)}
            Numeric Columns: {len(numeric_cols)}
            Categorical Columns: {len(df.select_dtypes(include=['object']).columns)}
            Missing Values: {df.isnull().sum().sum():,}
            Duplicate Rows: {df.duplicated().sum():,}
            """
            ax4.text(0.5, 0.5, stats_text, ha='center', va='center', fontsize=12, 
                    family='monospace', transform=ax4.transAxes)
            ax4.axis('off')
            ax4.set_title('Dataset Summary')
            
            fig.suptitle(f'{project.name} - Data Summary', fontsize=16, fontweight='bold')
            plt.tight_layout()
            filename = f'{safe_name}_summary'
        
        else:
            return Response({'detail': 'Invalid chart type'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save to buffer
        buffer = io.BytesIO()
        if export_format == 'svg':
            plt.savefig(buffer, format='svg', bbox_inches='tight', dpi=150)
            content_type = 'image/svg+xml'
            filename += '.svg'
        else:
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            content_type = 'image/png'
            filename += '.png'
        
        plt.close(fig)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        
        return Response({
            'filename': filename,
            'content_type': content_type,
            'content': image_base64,
            'encoding': 'base64'
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'detail': f'Export failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_pdf_report(request, project_id):
    """
    Export comprehensive analysis report as PDF
    """
    from .pdf_export import export_analysis_to_pdf
    from analysis.models import PipelineProgress
    
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get latest pipeline results
    try:
        progress = PipelineProgress.objects.filter(
            project=project,
            status='completed'
        ).order_by('-completed_at').first()
        
        if progress:
            results = progress.final_results
            llm_insights = progress.llm_insights
        else:
            # Fallback to project statistics
            results = {
                'summary': project.statistics.get('automation', {}).get('final_summary', {}),
                'cleaning': {},
                'statistics': project.statistics,
                'correlation': {},
                'insights': {},
                'visualization': {}
            }
            llm_insights = {}
    except Exception:
        results = {'summary': project.statistics}
        llm_insights = {}
    
    try:
        pdf_bytes = export_analysis_to_pdf(project.name, results, llm_insights)
        safe_name = project.name.replace(' ', '_').replace('"', '').replace("'", '')
        
        return Response({
            'filename': f'{safe_name}_analysis_report.pdf',
            'content_type': 'application/pdf',
            'content': base64.b64encode(pdf_bytes).decode('utf-8'),
            'encoding': 'base64'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'detail': f'PDF export failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_pipeline_pdf(request, pipeline_id):
    """
    Export pipeline results as PDF
    """
    from .pdf_export import export_analysis_to_pdf
    from analysis.models import PipelineProgress
    
    try:
        progress = PipelineProgress.objects.select_related('project').get(
            pipeline_id=pipeline_id,
            user=request.user
        )
    except PipelineProgress.DoesNotExist:
        return Response({'detail': 'Pipeline not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if progress.status != 'completed':
        return Response({'detail': 'Pipeline not completed yet'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        pdf_bytes = export_analysis_to_pdf(
            progress.project.name,
            progress.final_results,
            progress.llm_insights
        )
        safe_name = progress.project.name.replace(' ', '_').replace('"', '').replace("'", '')
        
        return Response({
            'filename': f'{safe_name}_pipeline_report.pdf',
            'content_type': 'application/pdf',
            'content': base64.b64encode(pdf_bytes).decode('utf-8'),
            'encoding': 'base64'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'detail': f'PDF export failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_pipeline_excel(request, pipeline_id):
    """
    Export pipeline results as Excel with multiple sheets
    """
    from analysis.models import PipelineProgress
    
    try:
        progress = PipelineProgress.objects.select_related('project').get(
            pipeline_id=pipeline_id,
            user=request.user
        )
    except PipelineProgress.DoesNotExist:
        return Response({'detail': 'Pipeline not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if progress.status != 'completed':
        return Response({'detail': 'Pipeline not completed yet'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        results = progress.final_results
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Summary sheet
            summary = results.get('summary', {})
            summary_data = {
                'Metric': ['Total Rows', 'Total Columns', 'Quality Score', 'Quality Label', 'Processing Time'],
                'Value': [
                    summary.get('total_rows', 0),
                    summary.get('total_columns', 0),
                    summary.get('quality_score', 'N/A'),
                    summary.get('quality_label', 'N/A'),
                    f"{progress.duration_seconds:.2f}s" if progress.duration_seconds else 'N/A'
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Statistics sheet
            statistics = results.get('statistics', {})
            numeric_summary = statistics.get('numeric_summary', {})
            if numeric_summary:
                stats_df = pd.DataFrame(numeric_summary).T
                stats_df.index.name = 'Column'
                stats_df.reset_index().to_excel(writer, sheet_name='Statistics', index=False)
            
            # Correlations sheet
            correlation = results.get('correlation', {})
            top_corr = correlation.get('top_correlations', [])
            if top_corr:
                corr_df = pd.DataFrame(top_corr)
                corr_df.to_excel(writer, sheet_name='Correlations', index=False)
            
            # Cleaning Actions sheet
            cleaning = results.get('cleaning', {})
            actions = cleaning.get('applied_actions', [])
            if actions:
                actions_df = pd.DataFrame(actions)
                actions_df.to_excel(writer, sheet_name='Cleaning Actions', index=False)
            
            # Insights sheet
            insights = results.get('insights', {})
            key_insights = insights.get('key_insights', [])
            if key_insights:
                insights_df = pd.DataFrame(key_insights)
                insights_df.to_excel(writer, sheet_name='Insights', index=False)
            
            # Visualization Recommendations sheet
            viz = results.get('visualization', {})
            suggestions = viz.get('suggested_visualizations', [])
            if suggestions:
                viz_df = pd.DataFrame(suggestions)
                viz_df.to_excel(writer, sheet_name='Visualizations', index=False)
            
            # LLM Insights sheet
            llm_insights = progress.llm_insights or {}
            if llm_insights:
                llm_data = [{'Section': k, 'Insight': v} for k, v in llm_insights.items() if v]
                if llm_data:
                    llm_df = pd.DataFrame(llm_data)
                    llm_df.to_excel(writer, sheet_name='AI Insights', index=False)
        
        buffer.seek(0)
        safe_name = progress.project.name.replace(' ', '_').replace('"', '').replace("'", '')
        
        return Response({
            'filename': f'{safe_name}_pipeline_report.xlsx',
            'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'content': base64.b64encode(buffer.getvalue()).decode('utf-8'),
            'encoding': 'base64'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'detail': f'Excel export failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_pipeline_csv(request, pipeline_id):
    """
    Export specific pipeline section as CSV
    """
    from analysis.models import PipelineProgress
    
    section = request.query_params.get('section', 'statistics')
    
    try:
        progress = PipelineProgress.objects.select_related('project').get(
            pipeline_id=pipeline_id,
            user=request.user
        )
    except PipelineProgress.DoesNotExist:
        return Response({'detail': 'Pipeline not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if progress.status != 'completed':
        return Response({'detail': 'Pipeline not completed yet'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        results = progress.final_results
        buffer = io.StringIO()
        safe_name = progress.project.name.replace(' ', '_').replace('"', '').replace("'", '')
        
        if section == 'statistics':
            statistics = results.get('statistics', {})
            numeric_summary = statistics.get('numeric_summary', {})
            if numeric_summary:
                df = pd.DataFrame(numeric_summary).T
                df.index.name = 'column'
                df.to_csv(buffer)
            filename = f'{safe_name}_statistics.csv'
            
        elif section == 'correlation':
            correlation = results.get('correlation', {})
            top_corr = correlation.get('top_correlations', [])
            if top_corr:
                df = pd.DataFrame(top_corr)
                df.to_csv(buffer, index=False)
            filename = f'{safe_name}_correlations.csv'
            
        elif section == 'cleaning':
            cleaning = results.get('cleaning', {})
            actions = cleaning.get('applied_actions', [])
            if actions:
                df = pd.DataFrame(actions)
                df.to_csv(buffer, index=False)
            filename = f'{safe_name}_cleaning_actions.csv'
            
        elif section == 'insights':
            insights = results.get('insights', {})
            key_insights = insights.get('key_insights', [])
            if key_insights:
                df = pd.DataFrame(key_insights)
                df.to_csv(buffer, index=False)
            filename = f'{safe_name}_insights.csv'
            
        elif section == 'visualizations':
            viz = results.get('visualization', {})
            recommendations = viz.get('smart_recommendations', {}).get('recommendations', [])
            if recommendations:
                df = pd.DataFrame(recommendations)
                df.to_csv(buffer, index=False)
            filename = f'{safe_name}_visualization_recommendations.csv'
            
        elif section == 'summary':
            summary = results.get('summary', {})
            summary_data = {
                'metric': ['Total Rows', 'Total Columns', 'Quality Score', 'Quality Label'],
                'value': [
                    summary.get('total_rows', 0),
                    summary.get('total_columns', 0),
                    summary.get('quality_score', 'N/A'),
                    summary.get('quality_label', 'N/A')
                ]
            }
            df = pd.DataFrame(summary_data)
            df.to_csv(buffer, index=False)
            filename = f'{safe_name}_summary.csv'
            
        else:
            return Response({'detail': f'Unknown section: {section}'}, status=status.HTTP_400_BAD_REQUEST)
        
        content = buffer.getvalue()
        
        return Response({
            'filename': filename,
            'content_type': 'text/csv',
            'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            'encoding': 'base64'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'detail': f'CSV export failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_chart_png(request, pipeline_id):
    """
    Export a specific chart as PNG based on recommendation
    """
    from analysis.models import PipelineProgress
    from analysis.chart_intelligence import ChartRecommendationEngine
    
    chart_type = request.query_params.get('chart_type', 'histogram')
    columns = request.query_params.getlist('columns', [])
    
    try:
        progress = PipelineProgress.objects.select_related('project').get(
            pipeline_id=pipeline_id,
            user=request.user
        )
    except PipelineProgress.DoesNotExist:
        return Response({'detail': 'Pipeline not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Load dataframe
    project = progress.project
    file_path = project.processed_file_path or project.file_path
    
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            return Response({'detail': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': f'Failed to load data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        safe_name = project.name.replace(' ', '_').replace('"', '').replace("'", '')
        
        if chart_type == 'histogram' and columns:
            col = columns[0]
            if col in df.columns:
                df[col].hist(ax=ax, bins=30, edgecolor='black', alpha=0.7)
                ax.set_xlabel(col)
                ax.set_ylabel('Frequency')
                ax.set_title(f'Distribution of {col}')
        
        elif chart_type == 'scatter_plot' and len(columns) >= 2:
            col1, col2 = columns[0], columns[1]
            if col1 in df.columns and col2 in df.columns:
                ax.scatter(df[col1], df[col2], alpha=0.6)
                ax.set_xlabel(col1)
                ax.set_ylabel(col2)
                ax.set_title(f'{col1} vs {col2}')
        
        elif chart_type == 'box_plot' and columns:
            col = columns[0]
            if col in df.columns:
                df.boxplot(column=col, ax=ax)
                ax.set_title(f'Box Plot of {col}')
        
        elif chart_type == 'bar_chart' and columns:
            col = columns[0]
            if col in df.columns:
                value_counts = df[col].value_counts().head(15)
                value_counts.plot(kind='bar', ax=ax, color='steelblue')
                ax.set_xlabel(col)
                ax.set_ylabel('Count')
                ax.set_title(f'Frequency of {col}')
                plt.xticks(rotation=45, ha='right')
        
        elif chart_type == 'correlation_matrix':
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) >= 2:
                corr_matrix = numeric_df.corr()
                sns.heatmap(corr_matrix, annot=len(numeric_df.columns) <= 8, 
                           cmap='RdBu_r', center=0, ax=ax)
                ax.set_title('Correlation Matrix')
        
        else:
            ax.text(0.5, 0.5, f'Chart type "{chart_type}" not supported', 
                   ha='center', va='center', fontsize=14)
        
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        plt.close(fig)
        buffer.seek(0)
        
        return Response({
            'filename': f'{safe_name}_{chart_type}.png',
            'content_type': 'image/png',
            'content': base64.b64encode(buffer.getvalue()).decode('utf-8'),
            'encoding': 'base64'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'detail': f'Chart export failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
