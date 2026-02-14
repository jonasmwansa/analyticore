from celery import shared_task
from django.utils import timezone
from django.conf import settings
import pandas as pd
import numpy as np
import os
import logging
import traceback

logger = logging.getLogger(__name__)


def convert_to_serializable(obj):
    """Convert numpy types to Python native types"""
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


@shared_task(bind=True, max_retries=3)
def execute_scheduled_pipeline(self, schedule_id):
    """Execute a scheduled pipeline"""
    from pipelines.models import ScheduledPipeline, PipelineRun
    from pipelines.context import PipelineContext
    from pipelines.base import Pipeline
    from pipelines.steps import ColumnUnderstandingStep
    
    try:
        schedule = ScheduledPipeline.objects.select_related('project').get(schedule_id=schedule_id)
    except ScheduledPipeline.DoesNotExist:
        logger.error(f"Scheduled pipeline not found: {schedule_id}")
        return {'status': 'error', 'message': 'Schedule not found'}
    
    # Create run record
    run = PipelineRun.objects.create(
        scheduled_pipeline=schedule,
        status='running',
        trigger='scheduled'
    )
    
    start_time = timezone.now()
    logs = []
    
    try:
        project = schedule.project
        logs.append(f"[{timezone.now().isoformat()}] Starting pipeline: {schedule.name}")
        logs.append(f"[{timezone.now().isoformat()}] Action type: {schedule.action_type}")
        logs.append(f"[{timezone.now().isoformat()}] Project: {project.name}")
        
        # Load data
        if not project.file_path or not os.path.exists(project.file_path):
            raise ValueError("No data file available for this project")
        
        logs.append(f"[{timezone.now().isoformat()}] Loading data from: {project.file_path}")
        
        if project.file_path.endswith('.csv'):
            df = pd.read_csv(project.file_path)
        elif project.file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(project.file_path)
        elif project.file_path.endswith('.json'):
            df = pd.read_json(project.file_path)
        else:
            raise ValueError(f"Unsupported file format: {project.file_path}")
        
        logs.append(f"[{timezone.now().isoformat()}] Loaded {len(df)} rows, {len(df.columns)} columns")
        
        # Execute based on action type
        if schedule.action_type == 'refresh_data':
            # Just reload and update statistics
            logs.append(f"[{timezone.now().isoformat()}] Refreshing data statistics...")
            statistics = generate_statistics(df)
            project.statistics = statistics
            project.row_count = len(df)
            project.column_count = len(df.columns)
            project.save()
            logs.append(f"[{timezone.now().isoformat()}] Statistics updated")
            
        elif schedule.action_type == 'run_analysis':
            # Run statistical analysis
            logs.append(f"[{timezone.now().isoformat()}] Running statistical analysis...")
            context = PipelineContext(
                project_id=str(project.project_id),
                original_df=df.copy(),
                current_df=df.copy()
            )
            pipeline = Pipeline("Scheduled Analysis")
            pipeline.add_step(ColumnUnderstandingStep())
            context = pipeline.execute(context)
            
            # Update project with new metadata
            statistics = generate_statistics(df, context.metadata)
            project.statistics = statistics
            project.save()
            logs.append(f"[{timezone.now().isoformat()}] Analysis completed")
            
        elif schedule.action_type == 'apply_cleaning':
            # Apply saved cleaning rules
            logs.append(f"[{timezone.now().isoformat()}] Applying cleaning rules...")
            cleaning_rules = schedule.pipeline_config.get('cleaning_rules', [])
            
            for rule in cleaning_rules:
                df = apply_cleaning_rule(df, rule, logs)
            
            # Save cleaned data
            output_path = os.path.join(
                settings.PIPELINE_STORAGE_PATH, 
                'processed', 
                f"{project.project_id}_cleaned_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            df.to_csv(output_path, index=False)
            project.processed_file_path = output_path
            project.save()
            run.output_file = output_path
            logs.append(f"[{timezone.now().isoformat()}] Cleaned data saved to: {output_path}")
            
        elif schedule.action_type == 'export_data':
            # Export data to specified format
            logs.append(f"[{timezone.now().isoformat()}] Exporting data...")
            export_format = schedule.pipeline_config.get('export_format', 'csv')
            output_path = export_data(df, project.project_id, export_format)
            run.output_file = output_path
            logs.append(f"[{timezone.now().isoformat()}] Exported to: {output_path}")
            
        elif schedule.action_type == 'full_pipeline':
            # Run full pipeline
            logs.append(f"[{timezone.now().isoformat()}] Running full pipeline...")
            
            # Step 1: Analysis
            context = PipelineContext(
                project_id=str(project.project_id),
                original_df=df.copy(),
                current_df=df.copy()
            )
            pipeline = Pipeline("Full Scheduled Pipeline")
            pipeline.add_step(ColumnUnderstandingStep())
            context = pipeline.execute(context)
            logs.append(f"[{timezone.now().isoformat()}] Analysis step completed")
            
            # Step 2: Apply cleaning rules if configured
            cleaning_rules = schedule.pipeline_config.get('cleaning_rules', [])
            for rule in cleaning_rules:
                df = apply_cleaning_rule(df, rule, logs)
            
            # Step 3: Save and export
            output_path = os.path.join(
                settings.PIPELINE_STORAGE_PATH, 
                'processed', 
                f"{project.project_id}_full_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            df.to_csv(output_path, index=False)
            project.processed_file_path = output_path
            
            # Update statistics
            statistics = generate_statistics(df, context.metadata)
            project.statistics = statistics
            project.row_count = len(df)
            project.column_count = len(df.columns)
            project.status = 'transformed'
            project.save()
            
            run.output_file = output_path
            logs.append(f"[{timezone.now().isoformat()}] Full pipeline completed")
        
        # Mark run as completed
        run.status = 'completed'
        run.rows_processed = len(df)
        run.transformations_applied = len(schedule.pipeline_config.get('cleaning_rules', []))
        
        # Reset consecutive failures
        schedule.consecutive_failures = 0
        
        logs.append(f"[{timezone.now().isoformat()}] Pipeline completed successfully")
        
    except Exception as e:
        run.status = 'failed'
        run.error_message = str(e)
        logs.append(f"[{timezone.now().isoformat()}] ERROR: {str(e)}")
        logs.append(f"[{timezone.now().isoformat()}] Traceback: {traceback.format_exc()}")
        logger.error(f"Pipeline run {run.run_id} failed: {str(e)}")
        
        # Track consecutive failures
        schedule.consecutive_failures += 1
        if schedule.consecutive_failures >= 3:
            schedule.status = 'failed'
            logs.append(f"[{timezone.now().isoformat()}] Pipeline paused after 3 consecutive failures")
    
    # Finalize run record
    end_time = timezone.now()
    run.completed_at = end_time
    run.duration_seconds = int((end_time - start_time).total_seconds())
    run.logs = '\n'.join(logs)
    run.save()
    
    # Update schedule
    schedule.last_run = end_time
    schedule.run_count += 1
    schedule.save()
    
    # Always send notification for pipeline completion/failure
    send_pipeline_notification(schedule, run)
    
    return {
        'status': run.status,
        'run_id': str(run.run_id),
        'duration': run.duration_seconds,
        'rows_processed': run.rows_processed
    }


def generate_statistics(df, metadata=None):
    """Generate statistics for a dataframe"""
    stats = {
        'total_rows': int(len(df)),
        'total_columns': int(len(df.columns)),
        'columns': df.columns.tolist(),
        'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'missing_values': {col: int(v) for col, v in df.isnull().sum().items()},
    }
    
    # Add sample data
    sample_data = []
    for _, row in df.head(5).iterrows():
        record = {}
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                record[col] = None
            elif isinstance(val, (np.integer, np.int64)):
                record[col] = int(val)
            elif isinstance(val, (np.floating, np.float64)):
                record[col] = float(val) if not np.isnan(val) else None
            else:
                record[col] = val
        sample_data.append(record)
    stats['sample_data'] = sample_data
    
    # Add column metadata if available
    if metadata:
        stats['column_metadata'] = {
            name: convert_to_serializable({
                'inferred_type': meta.inferred_type,
                'confidence': meta.confidence,
                'missing_percentage': meta.missing_percentage,
                'unique_count': meta.unique_count,
                'is_identifier': meta.is_identifier,
                'statistics': meta.statistics
            }) for name, meta in metadata.items()
        }
    
    return stats


def apply_cleaning_rule(df, rule, logs):
    """Apply a single cleaning rule to the dataframe"""
    column = rule.get('column')
    action = rule.get('action')
    params = rule.get('parameters', {})
    
    logs.append(f"[{timezone.now().isoformat()}] Applying {action} to column {column}")
    
    if action == 'fill_mean' and column in df.columns:
        df[column] = df[column].fillna(df[column].mean())
    elif action == 'fill_median' and column in df.columns:
        df[column] = df[column].fillna(df[column].median())
    elif action == 'fill_mode' and column in df.columns:
        mode_val = df[column].mode()
        if len(mode_val) > 0:
            df[column] = df[column].fillna(mode_val[0])
    elif action == 'drop_nulls' and column in df.columns:
        df = df.dropna(subset=[column])
    elif action == 'remove_duplicates':
        df = df.drop_duplicates()
    elif action == 'remove_outliers' and column in df.columns:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        df = df[(df[column] >= Q1 - 1.5 * IQR) & (df[column] <= Q3 + 1.5 * IQR)]
    
    return df


def export_data(df, project_id, format='csv'):
    """Export dataframe to specified format"""
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    export_dir = os.path.join(settings.PIPELINE_STORAGE_PATH, 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    if format == 'csv':
        path = os.path.join(export_dir, f"{project_id}_{timestamp}.csv")
        df.to_csv(path, index=False)
    elif format == 'xlsx':
        path = os.path.join(export_dir, f"{project_id}_{timestamp}.xlsx")
        df.to_excel(path, index=False)
    elif format == 'json':
        path = os.path.join(export_dir, f"{project_id}_{timestamp}.json")
        df.to_json(path, orient='records')
    else:
        path = os.path.join(export_dir, f"{project_id}_{timestamp}.csv")
        df.to_csv(path, index=False)
    
    return path


def send_pipeline_notification(schedule, run):
    """Send notification about pipeline completion"""
    try:
        from users.notification_service import NotificationService
        
        if run.status == 'completed':
            notification_type = 'pipeline_complete'
            title = f"Pipeline '{schedule.name}' completed successfully"
            message = f"Your scheduled pipeline processed {run.rows_processed:,} rows in {run.duration_seconds or 0} seconds.\n\nProject: {schedule.project.name}\nAction: {schedule.get_action_type_display()}"
            priority = 'low'
        else:
            notification_type = 'pipeline_failed'
            title = f"Pipeline '{schedule.name}' failed"
            error_preview = run.error_message[:200] if run.error_message else 'Unknown error'
            message = f"Your scheduled pipeline encountered an error.\n\nProject: {schedule.project.name}\nError: {error_preview}"
            priority = 'high'
        
        NotificationService.create_notification(
            user=schedule.user,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            related_project_id=schedule.project.project_id,
            related_object_type='pipeline_run',
            related_object_id=run.run_id,
            metadata={
                'schedule_id': str(schedule.schedule_id),
                'run_id': str(run.run_id),
                'project_id': str(schedule.project.project_id),
                'action_type': schedule.action_type,
                'rows_processed': run.rows_processed,
                'duration_seconds': run.duration_seconds,
                'status': run.status
            },
            send_email=True,
            send_push=True
        )
        logger.info(f"Pipeline notification sent to {schedule.user.email} for run {run.run_id}")
    except Exception as e:
        logger.error(f"Failed to send pipeline notification: {str(e)}")


@shared_task
def run_pipeline_manually(schedule_id, user_id=None):
    """Trigger a manual run of a scheduled pipeline"""
    from pipelines.models import ScheduledPipeline, PipelineRun
    
    try:
        schedule = ScheduledPipeline.objects.get(schedule_id=schedule_id)
        
        # Create run with manual trigger
        run = PipelineRun.objects.create(
            scheduled_pipeline=schedule,
            status='pending',
            trigger='manual'
        )
        
        # Execute the pipeline
        result = execute_scheduled_pipeline(schedule_id)
        
        return result
        
    except ScheduledPipeline.DoesNotExist:
        return {'status': 'error', 'message': 'Schedule not found'}
