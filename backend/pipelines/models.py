from django.db import models
from django.conf import settings
from projects.models import Project
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule
import uuid
import json


class ScheduledPipeline(models.Model):
    """User-defined scheduled data pipeline"""
    
    SCHEDULE_TYPES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom Cron'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('failed', 'Failed'),
    ]
    
    ACTION_TYPES = [
        ('refresh_data', 'Refresh Data from Source'),
        ('run_analysis', 'Run Statistical Analysis'),
        ('apply_cleaning', 'Apply Data Cleaning Rules'),
        ('export_data', 'Export Data'),
        ('full_pipeline', 'Full Pipeline (Refresh + Analysis + Export)'),
    ]
    
    schedule_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scheduled_pipelines')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='schedules')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Schedule configuration
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES, default='daily')
    
    # For preset schedules
    hour = models.IntegerField(default=0, help_text="Hour to run (0-23)")
    minute = models.IntegerField(default=0, help_text="Minute to run (0-59)")
    day_of_week = models.CharField(max_length=20, default='*', help_text="Day of week (0-6 or mon-sun)")
    day_of_month = models.CharField(max_length=20, default='*', help_text="Day of month (1-31)")
    
    # For custom cron
    cron_expression = models.CharField(max_length=100, blank=True, help_text="Custom cron: minute hour day month weekday")
    
    # Action configuration
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES, default='run_analysis')
    pipeline_config = models.JSONField(default=dict, help_text="Additional pipeline configuration")
    
    # Status tracking
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Run tracking
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    run_count = models.IntegerField(default=0)
    consecutive_failures = models.IntegerField(default=0)
    
    # Link to Celery Beat
    celery_task = models.OneToOneField(
        PeriodicTask, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='scheduled_pipeline'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduled_pipelines'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['project', 'is_active']),
            models.Index(fields=['next_run']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_schedule_type_display()}"
    
    def get_crontab_schedule(self):
        """Get or create a CrontabSchedule for this pipeline"""
        if self.schedule_type == 'hourly':
            return CrontabSchedule.objects.get_or_create(
                minute=str(self.minute),
                hour='*',
                day_of_week='*',
                day_of_month='*',
                month_of_year='*'
            )[0]
        elif self.schedule_type == 'daily':
            return CrontabSchedule.objects.get_or_create(
                minute=str(self.minute),
                hour=str(self.hour),
                day_of_week='*',
                day_of_month='*',
                month_of_year='*'
            )[0]
        elif self.schedule_type == 'weekly':
            return CrontabSchedule.objects.get_or_create(
                minute=str(self.minute),
                hour=str(self.hour),
                day_of_week=self.day_of_week,
                day_of_month='*',
                month_of_year='*'
            )[0]
        elif self.schedule_type == 'monthly':
            return CrontabSchedule.objects.get_or_create(
                minute=str(self.minute),
                hour=str(self.hour),
                day_of_week='*',
                day_of_month=self.day_of_month,
                month_of_year='*'
            )[0]
        elif self.schedule_type == 'custom' and self.cron_expression:
            parts = self.cron_expression.split()
            if len(parts) >= 5:
                return CrontabSchedule.objects.get_or_create(
                    minute=parts[0],
                    hour=parts[1],
                    day_of_month=parts[2],
                    month_of_year=parts[3],
                    day_of_week=parts[4]
                )[0]
        return None
    
    def sync_celery_task(self):
        """Create or update the Celery Beat periodic task"""
        crontab = self.get_crontab_schedule()
        if not crontab:
            return
        
        task_name = f'scheduled_pipeline_{self.schedule_id}'
        
        task_kwargs = json.dumps({
            'schedule_id': str(self.schedule_id)
        })
        
        if self.celery_task:
            # Update existing task
            self.celery_task.crontab = crontab
            self.celery_task.kwargs = task_kwargs
            self.celery_task.enabled = self.is_active and self.status == 'active'
            self.celery_task.save()
        else:
            # Create new task
            periodic_task = PeriodicTask.objects.create(
                crontab=crontab,
                name=task_name,
                task='pipelines.tasks.execute_scheduled_pipeline',
                kwargs=task_kwargs,
                enabled=self.is_active and self.status == 'active'
            )
            self.celery_task = periodic_task
            self.save(update_fields=['celery_task'])
    
    def delete_celery_task(self):
        """Delete the associated Celery Beat task"""
        if self.celery_task:
            self.celery_task.delete()
            self.celery_task = None


class PipelineRun(models.Model):
    """Record of each pipeline execution"""
    
    RUN_STATUS = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    run_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    scheduled_pipeline = models.ForeignKey(
        ScheduledPipeline, 
        on_delete=models.CASCADE, 
        related_name='runs'
    )
    status = models.CharField(max_length=20, choices=RUN_STATUS, default='pending')
    trigger = models.CharField(max_length=50, default='scheduled', help_text="scheduled or manual")
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Results
    rows_processed = models.IntegerField(default=0)
    transformations_applied = models.IntegerField(default=0)
    output_file = models.CharField(max_length=500, blank=True)
    
    # Logs and errors
    logs = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'pipeline_runs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['scheduled_pipeline', '-started_at']),
            models.Index(fields=['status']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        return f"Run {self.run_id} - {self.status}"
