from celery import shared_task
from django.utils import timezone
from pipelines.scheduled_models import ScheduledPipeline, PipelineRun
from pipelines.context import PipelineContext
from pipelines.base import Pipeline
import pandas as pd
import logging

logger = logging.getLogger(__name__)

@shared_task
def execute_scheduled_pipeline(schedule_id):
    """Execute a scheduled pipeline"""
    try:
        schedule = ScheduledPipeline.objects.get(schedule_id=schedule_id)
        run = PipelineRun.objects.create(
            scheduled_pipeline=schedule,
            status='running'
        )
        
        start_time = timezone.now()
        
        try:
            project = schedule.project
            if not project.file_path:
                raise ValueError("No data file available")
            
            if project.file_path.endswith('.csv'):
                df = pd.read_csv(project.file_path)
            elif project.file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(project.file_path)
            else:
                df = pd.read_json(project.file_path)
            
            context = PipelineContext(
                project_id=str(project.project_id),
                original_df=df.copy(),
                current_df=df.copy(),
                config=schedule.pipeline_config
            )
            
            pipeline = Pipeline(f"Scheduled: {schedule.name}")
            
            context = pipeline.execute(context)
            
            run.status = 'completed'
            run.rows_processed = len(context.current_df)
            run.transformations_applied = len(context.change_log)
            run.logs = f"Processed {len(context.current_df)} rows with {len(context.change_log)} transformations"
            
        except Exception as e:
            run.status = 'failed'
            run.error_message = str(e)
            logger.error(f"Pipeline run {run.run_id} failed: {str(e)}")
        
        end_time = timezone.now()
        run.completed_at = end_time
        run.duration_seconds = int((end_time - start_time).total_seconds())
        run.save()
        
        schedule.last_run = end_time
        schedule.run_count += 1
        schedule.save()
        
    except Exception as e:
        logger.error(f"Failed to execute scheduled pipeline: {str(e)}")

@shared_task
def check_and_run_scheduled_pipelines():
    """Check for pipelines that need to run"""
    now = timezone.now()
    schedules = ScheduledPipeline.objects.filter(
        is_active=True,
        status='active',
        next_run__lte=now
    )
    
    for schedule in schedules:
        execute_scheduled_pipeline.delay(str(schedule.schedule_id))