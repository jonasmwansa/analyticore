from django.db import models
from projects.models import Project
import uuid

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