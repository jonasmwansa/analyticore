from django.db import models
from projects.models import Project
import uuid

class ScheduledPipeline(models.Model):
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
    
    schedule_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='schedules')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES)
    cron_expression = models.CharField(max_length=100, blank=True, help_text="For custom schedules")
    
    pipeline_config = models.JSONField(default=dict, help_text="Pipeline configuration")
    
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    run_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduled_pipelines'
        indexes = [
            models.Index(fields=['project', 'is_active']),
            models.Index(fields=['next_run']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.schedule_type}"

class PipelineRun(models.Model):
    RUN_STATUS = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    run_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    scheduled_pipeline = models.ForeignKey(ScheduledPipeline, on_delete=models.CASCADE, related_name='runs')
    status = models.CharField(max_length=20, choices=RUN_STATUS, default='pending')
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    logs = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    rows_processed = models.IntegerField(default=0)
    transformations_applied = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'pipeline_runs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['scheduled_pipeline', '-started_at']),
            models.Index(fields=['status']),
        ]