from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project
import uuid

User = get_user_model()


class PipelineProgress(models.Model):
    """Track progress of automated analysis pipeline with cancel/pause support"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    
    STAGE_CHOICES = [
        ('ingestion', 'Data Ingestion'),
        ('profiling', 'Data Profiling'),
        ('cleaning', 'Data Cleaning'),
        ('transformation', 'Transformation'),
        ('statistics', 'Statistical Analysis'),
        ('correlation', 'Correlation Analysis'),
        ('insights', 'AI Insights'),
        ('visualization', 'Visualization'),
        ('summary', 'Executive Summary'),
    ]
    
    pipeline_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pipeline_runs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pipeline_runs')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    current_stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='ingestion')
    progress_percent = models.IntegerField(default=0)
    
    # Control flags
    cancel_requested = models.BooleanField(default=False)
    pause_requested = models.BooleanField(default=False)
    
    # Results storage
    stages_completed = models.JSONField(default=list)  # List of completed stage results
    current_stage_data = models.JSONField(default=dict)  # Current stage progress data
    final_results = models.JSONField(default=dict)  # Final analysis results
    error_message = models.TextField(blank=True, null=True)
    
    # LLM insights
    llm_enabled = models.BooleanField(default=True)
    llm_insights = models.JSONField(default=dict)  # AI-generated insights per stage
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pipeline_progress'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pipeline {self.pipeline_id} - {self.project.name} ({self.status})"
    
    @property
    def duration_seconds(self):
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def request_cancel(self):
        self.cancel_requested = True
        self.save(update_fields=['cancel_requested'])
    
    def request_pause(self):
        self.pause_requested = True
        self.save(update_fields=['pause_requested'])
    
    def resume(self):
        if self.status == 'paused':
            self.pause_requested = False
            self.status = 'running'
            self.save(update_fields=['pause_requested', 'status'])
    
    def update_stage(self, stage: str, progress: int, data: dict = None):
        self.current_stage = stage
        self.progress_percent = progress
        if data:
            self.current_stage_data = data
        self.save(update_fields=['current_stage', 'progress_percent', 'current_stage_data', 'updated_at'])
    
    def complete_stage(self, stage: str, result: dict):
        completed = self.stages_completed or []
        completed.append({
            'stage': stage,
            'result': result,
            'completed_at': str(self.updated_at)
        })
        self.stages_completed = completed
        self.save(update_fields=['stages_completed', 'updated_at'])


class AnalysisRun(models.Model):
    analysis_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='analyses')
    recommendations = models.JSONField(default=list)
    statistics = models.JSONField(default=dict)
    change_log = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analysis_runs'
        ordering = ['-created_at']

class TransformationLog(models.Model):
    log_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='transformations')
    step_name = models.CharField(max_length=255)
    action = models.CharField(max_length=100)
    target = models.CharField(max_length=255)
    reason = models.TextField()
    impact = models.JSONField(default=dict)
    confidence = models.FloatField()
    reversible = models.BooleanField(default=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transformation_logs'
        ordering = ['-applied_at']