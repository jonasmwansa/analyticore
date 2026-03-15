"""
Pipeline Runner - Orchestrates the automated analysis pipeline with progress tracking
Supports cancel/pause functionality and integrates local LLM for insights
"""
import os
import time
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Callable
from django.utils import timezone
from django.db import transaction

from .models import PipelineProgress, AnalysisRun, TransformationLog
from .local_llm_service import LocalLLMService, get_llm_status
from .magic_analysis_service import run_magic_analysis
from .statistics import StatisticalAnalyzer
from .insights import generate_cleaning_recommendations_without_ai
from .services import TransformationService
from pipelines.base import Pipeline
from pipelines.context import PipelineContext
from pipelines.steps import ColumnUnderstandingStep

logger = logging.getLogger(__name__)


def _convert_to_serializable(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {key: _convert_to_serializable(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_convert_to_serializable(value) for value in obj]
    if isinstance(obj, tuple):
        return [_convert_to_serializable(value) for value in obj]
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj) if not np.isnan(obj) else None
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.bool_):
        return bool(obj)
    if pd.isna(obj):
        return None
    return obj


class PipelineRunner:
    """
    Runs the automated analysis pipeline with real-time progress tracking,
    cancel/pause support, and local LLM-powered insights.
    """
    
    STAGES = [
        ('ingestion', 'Data Ingestion', 10),
        ('profiling', 'Data Profiling', 20),
        ('cleaning', 'Data Cleaning', 35),
        ('transformation', 'Transformation', 45),
        ('statistics', 'Statistical Analysis', 60),
        ('correlation', 'Correlation Analysis', 70),
        ('insights', 'AI Insights', 85),
        ('visualization', 'Visualization', 92),
        ('summary', 'Executive Summary', 100),
    ]
    
    def __init__(self, progress: PipelineProgress, df: pd.DataFrame, project):
        self.progress = progress
        self.df = df.copy()
        self.original_df = df.copy()
        self.project = project
        self.results = {}
        self.llm = LocalLLMService() if progress.llm_enabled else None
    
    def check_control_flags(self) -> str:
        """Check for cancel/pause requests. Returns 'continue', 'paused', or 'cancelled'"""
        self.progress.refresh_from_db()
        
        if self.progress.cancel_requested:
            self.progress.status = 'cancelled'
            self.progress.completed_at = timezone.now()
            self.progress.save()
            return 'cancelled'
        
        if self.progress.pause_requested:
            self.progress.status = 'paused'
            self.progress.save()
            return 'paused'
        
        return 'continue'
    
    def run(self) -> Dict[str, Any]:
        """Execute the full pipeline with progress tracking"""
        try:
            self.progress.status = 'running'
            self.progress.started_at = timezone.now()
            self.progress.save()
            
            # Execute each stage
            for stage_key, stage_name, progress_pct in self.STAGES:
                # Check control flags before each stage
                control = self.check_control_flags()
                if control == 'cancelled':
                    return {'status': 'cancelled', 'message': 'Pipeline was cancelled by user'}
                if control == 'paused':
                    return {'status': 'paused', 'message': 'Pipeline paused', 'current_stage': stage_key}
                
                # Update progress
                self.progress.update_stage(stage_key, progress_pct, {'stage_name': stage_name})
                
                # Execute stage
                try:
                    result = self._execute_stage(stage_key)
                    self.results[stage_key] = result
                    self.progress.complete_stage(stage_key, _convert_to_serializable(result))
                except Exception as e:
                    logger.error(f"Stage {stage_key} failed: {e}", exc_info=True)
                    self.progress.status = 'failed'
                    self.progress.error_message = f"Stage '{stage_name}' failed: {str(e)}"
                    self.progress.save()
                    return {'status': 'failed', 'error': str(e), 'stage': stage_key}
            
            # Complete pipeline
            self.progress.status = 'completed'
            self.progress.progress_percent = 100
            self.progress.completed_at = timezone.now()
            self.progress.final_results = _convert_to_serializable(self.results)
            self.progress.save()
            
            # Save analysis run
            self._save_analysis_run()
            
            return {
                'status': 'completed',
                'results': _convert_to_serializable(self.results),
                'duration_seconds': self.progress.duration_seconds
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            self.progress.status = 'failed'
            self.progress.error_message = str(e)
            self.progress.save()
            return {'status': 'failed', 'error': str(e)}
    
    def _execute_stage(self, stage_key: str) -> Dict[str, Any]:
        """Execute a specific pipeline stage"""
        stage_methods = {
            'ingestion': self._stage_ingestion,
            'profiling': self._stage_profiling,
            'cleaning': self._stage_cleaning,
            'transformation': self._stage_transformation,
            'statistics': self._stage_statistics,
            'correlation': self._stage_correlation,
            'insights': self._stage_insights,
            'visualization': self._stage_visualization,
            'summary': self._stage_summary,
        }
        
        method = stage_methods.get(stage_key)
        if method:
            return method()
        return {}
    
    def _stage_ingestion(self) -> Dict[str, Any]:
        """Stage 1: Data Ingestion - Validate and load data"""
        rows, cols = self.df.shape
        dtypes = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        
        return {
            'status': 'completed',
            'rows': rows,
            'columns': cols,
            'column_names': self.df.columns.tolist(),
            'data_types': dtypes,
            'memory_usage_mb': round(self.df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            'message': f"Successfully loaded {rows:,} rows and {cols} columns"
        }
    
    def _stage_profiling(self) -> Dict[str, Any]:
        """Stage 2: Data Profiling - Understand column characteristics"""
        context = PipelineContext(
            project_id=str(self.project.project_id),
            original_df=self.df.copy(),
            current_df=self.df.copy(),
        )
        pipeline = Pipeline("Profiling")
        pipeline.add_step(ColumnUnderstandingStep())
        context = pipeline.execute(context)
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        
        profile = {
            'numeric_columns': numeric_cols,
            'categorical_columns': categorical_cols,
            'datetime_columns': datetime_cols,
            'column_metadata': {}
        }
        
        if hasattr(context, 'metadata') and context.metadata:
            for name, meta in context.metadata.items():
                profile['column_metadata'][name] = _convert_to_serializable({
                    'inferred_type': getattr(meta, 'inferred_type', 'unknown'),
                    'confidence': getattr(meta, 'confidence', 0),
                    'missing_percentage': getattr(meta, 'missing_percentage', 0),
                    'unique_count': getattr(meta, 'unique_count', 0),
                    'statistics': getattr(meta, 'statistics', {}),
                })
        
        return profile
    
    def _stage_cleaning(self) -> Dict[str, Any]:
        """Stage 3: Data Cleaning - Identify and fix data quality issues"""
        # Generate recommendations
        recommendations = generate_cleaning_recommendations_without_ai(self.df)
        
        # Run magic analysis to get cleaning suggestions
        magic_result = run_magic_analysis(self.df, self.project.name)
        cleaning_suggestions = magic_result.get('cleaning_suggestions', [])
        data_quality = magic_result.get('data_quality', {})
        
        # Auto-apply recommended cleaning actions
        applied_actions = []
        for suggestion in cleaning_suggestions:
            options = suggestion.get('options', [])
            recommended = next((opt for opt in options if opt.get('recommended')), None)
            
            if recommended and suggestion.get('priority') in ['high', 'medium']:
                action = self._apply_cleaning_action(suggestion, recommended)
                if action:
                    applied_actions.append(action)
        
        # Generate LLM insight if available
        llm_insight = ""
        if self.llm and self.llm.is_available:
            issues = data_quality.get('issues', [])
            llm_insight = self.llm.generate_cleaning_insights(self.df, issues)
            self.progress.llm_insights['cleaning'] = llm_insight
            self.progress.save(update_fields=['llm_insights'])
        
        return {
            'recommendations': _convert_to_serializable(recommendations),
            'cleaning_suggestions': _convert_to_serializable(cleaning_suggestions),
            'data_quality': _convert_to_serializable(data_quality),
            'applied_actions': applied_actions,
            'rows_before': len(self.original_df),
            'rows_after': len(self.df),
            'llm_insight': llm_insight,
            'message': f"Applied {len(applied_actions)} cleaning actions"
        }
    
    def _apply_cleaning_action(self, suggestion: Dict, option: Dict) -> Optional[Dict]:
        """Apply a single cleaning action"""
        column = suggestion.get('column')
        issue = suggestion.get('issue')
        strategy = option.get('strategy')
        
        try:
            if issue == 'missing_values' and column in self.df.columns:
                original_missing = int(self.df[column].isnull().sum())
                
                if strategy == 'mean':
                    self.df[column] = self.df[column].fillna(self.df[column].mean())
                elif strategy == 'median':
                    self.df[column] = self.df[column].fillna(self.df[column].median())
                elif strategy == 'mode':
                    mode = self.df[column].mode()
                    if len(mode) > 0:
                        self.df[column] = self.df[column].fillna(mode.iloc[0])
                elif strategy == 'forward_fill':
                    self.df[column] = self.df[column].fillna(method='ffill')
                elif strategy == 'drop_rows':
                    self.df = self.df.dropna(subset=[column])
                
                return {
                    'column': column,
                    'issue': issue,
                    'strategy': strategy,
                    'values_affected': original_missing
                }
            
            elif issue == 'duplicates' and column == '__all__':
                rows_before = len(self.df)
                self.df = self.df.drop_duplicates()
                return {
                    'column': '__all__',
                    'issue': 'duplicates',
                    'strategy': strategy,
                    'rows_removed': rows_before - len(self.df)
                }
            
        except Exception as e:
            logger.warning(f"Failed to apply cleaning action: {e}")
        
        return None
    
    def _stage_transformation(self) -> Dict[str, Any]:
        """Stage 4: Transformation - Prepare data for analysis"""
        transformations = []
        
        # Type conversions for numeric columns stored as strings
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                try:
                    numeric = pd.to_numeric(self.df[col], errors='coerce')
                    valid_pct = numeric.notna().sum() / len(self.df) * 100
                    if valid_pct > 90:
                        self.df[col] = numeric
                        transformations.append({
                            'column': col,
                            'action': 'to_numeric',
                            'valid_percentage': round(valid_pct, 2)
                        })
                except Exception:
                    pass
        
        # Save processed file
        output_path = None
        try:
            output_path, backup_path = TransformationService.save_processed_data(
                self.df, self.project.project_id
            )
            self.project.processed_file_path = output_path
            self.project.save(update_fields=['processed_file_path'])
        except Exception as e:
            logger.warning(f"Failed to save processed data: {e}")
        
        return {
            'transformations_applied': transformations,
            'processed_file_path': output_path,
            'final_shape': list(self.df.shape),
            'message': f"Applied {len(transformations)} transformations"
        }
    
    def _stage_statistics(self) -> Dict[str, Any]:
        """Stage 5: Statistical Analysis"""
        analyzer = StatisticalAnalyzer(self.df)
        stats = analyzer.get_descriptive_statistics()
        
        return _convert_to_serializable(stats)
    
    def _stage_correlation(self) -> Dict[str, Any]:
        """Stage 6: Correlation Analysis"""
        analyzer = StatisticalAnalyzer(self.df)
        correlation = analyzer.get_correlation_matrix()
        
        # Generate LLM insight
        llm_insight = ""
        if self.llm and self.llm.is_available:
            top_corr = correlation.get('top_correlations', [])
            llm_insight = self.llm.generate_correlation_insights(top_corr)
            self.progress.llm_insights['correlation'] = llm_insight
            self.progress.save(update_fields=['llm_insights'])
        
        result = _convert_to_serializable(correlation)
        result['llm_insight'] = llm_insight
        return result
    
    def _stage_insights(self) -> Dict[str, Any]:
        """Stage 7: AI-Powered Insights"""
        magic_result = run_magic_analysis(self.df, self.project.name)
        key_insights = magic_result.get('key_insights', [])
        
        # Enhance with LLM
        llm_insights = {}
        if self.llm and self.llm.is_available:
            # Executive insight
            stats = self.results.get('statistics', {})
            exec_insight = self.llm.generate_executive_summary(self.df, stats)
            llm_insights['executive'] = exec_insight
            
            # Visualization insight
            viz_insight = self.llm.generate_visualization_recommendations(self.df, key_insights)
            llm_insights['visualization'] = viz_insight
            
            self.progress.llm_insights['insights'] = llm_insights
            self.progress.save(update_fields=['llm_insights'])
        
        return {
            'key_insights': _convert_to_serializable(key_insights),
            'llm_insights': llm_insights,
            'insights_count': len(key_insights)
        }
    
    def _stage_visualization(self) -> Dict[str, Any]:
        """Stage 8: Visualization Recommendations with Smart Chart Intelligence"""
        from .chart_intelligence import get_smart_chart_recommendations
        
        # Get smart chart recommendations based on data analysis
        smart_recommendations = get_smart_chart_recommendations(self.df)
        
        # Also get magic analysis suggestions for backward compatibility
        magic_result = run_magic_analysis(self.df, self.project.name)
        magic_suggestions = magic_result.get('suggested_visualizations', [])
        
        # Generate LLM narratives for top recommendations
        llm_chart_insights = {}
        if self.llm and self.llm.is_available:
            for rec in smart_recommendations.get('recommendations', [])[:3]:
                narrative = self.llm.generate_chart_narrative(
                    chart_type=rec['chart_type'],
                    columns=rec['columns'],
                    data_summary=smart_recommendations.get('data_summary', {}),
                    chart_config=rec.get('config', {})
                )
                llm_chart_insights[rec['chart_type']] = {
                    'title': rec['title'],
                    'narrative': narrative,
                    'reasoning': rec['reasoning']
                }
            
            self.progress.llm_insights['visualization'] = llm_chart_insights
            self.progress.save(update_fields=['llm_insights'])
        
        return {
            'smart_recommendations': _convert_to_serializable(smart_recommendations),
            'suggested_visualizations': _convert_to_serializable(magic_suggestions),
            'column_profiles': smart_recommendations.get('column_profiles', {}),
            'best_chart_types': smart_recommendations.get('data_summary', {}).get('best_chart_types', []),
            'llm_chart_insights': llm_chart_insights,
            'count': len(smart_recommendations.get('recommendations', []))
        }
    
    def _stage_summary(self) -> Dict[str, Any]:
        """Stage 9: Executive Summary"""
        magic_result = run_magic_analysis(self.df, self.project.name)
        executive = magic_result.get('executive_summary', {})
        next_steps = magic_result.get('next_steps', [])
        
        # LLM-enhanced summary
        llm_summary = ""
        if self.llm and self.llm.is_available:
            stats = self.results.get('statistics', {})
            llm_summary = self.llm.generate_executive_summary(self.df, stats)
            self.progress.llm_insights['summary'] = llm_summary
            self.progress.save(update_fields=['llm_insights'])
        
        # Build final summary
        summary = {
            'executive_summary': _convert_to_serializable(executive),
            'next_steps': _convert_to_serializable(next_steps),
            'llm_summary': llm_summary,
            'quality_score': executive.get('quality_score', 0),
            'quality_label': executive.get('quality_label', 'unknown'),
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'processing_time_seconds': self.progress.duration_seconds
        }
        
        # Update project
        self.project.statistics = summary
        self.project.row_count = len(self.df)
        self.project.column_count = len(self.df.columns)
        self.project.status = 'completed'
        self.project.completed_at = timezone.now()
        self.project.save()
        
        return summary
    
    def _save_analysis_run(self):
        """Save analysis results to database"""
        AnalysisRun.objects.create(
            project=self.project,
            recommendations=self.results.get('cleaning', {}).get('recommendations', []),
            statistics=_convert_to_serializable(self.results),
            change_log=self.progress.stages_completed or []
        )


def start_pipeline(project, df: pd.DataFrame, user, llm_enabled: bool = True) -> PipelineProgress:
    """Start a new automated analysis pipeline"""
    progress = PipelineProgress.objects.create(
        project=project,
        user=user,
        llm_enabled=llm_enabled,
        status='pending'
    )
    return progress


def run_pipeline(progress: PipelineProgress, df: pd.DataFrame, project) -> Dict[str, Any]:
    """Run the pipeline (call this in a background task or synchronously)"""
    runner = PipelineRunner(progress, df, project)
    return runner.run()


def get_pipeline_status(pipeline_id: str) -> Optional[Dict[str, Any]]:
    """Get current status of a pipeline"""
    try:
        progress = PipelineProgress.objects.get(pipeline_id=pipeline_id)
        return {
            'pipeline_id': str(progress.pipeline_id),
            'status': progress.status,
            'current_stage': progress.current_stage,
            'progress_percent': progress.progress_percent,
            'stages_completed': progress.stages_completed,
            'current_stage_data': progress.current_stage_data,
            'llm_insights': progress.llm_insights,
            'error_message': progress.error_message,
            'started_at': progress.started_at.isoformat() if progress.started_at else None,
            'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
            'duration_seconds': progress.duration_seconds,
            'final_results': progress.final_results if progress.status == 'completed' else None,
        }
    except PipelineProgress.DoesNotExist:
        return None
