from django.db import models
from django.conf import settings
import uuid

class Project(models.Model):
    SOURCE_TYPES = [
        ('file_upload', 'File Upload'),
        ('database', 'Database Connection'),
        ('api', 'API Integration'),
    ]
    
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('uploaded', 'Data Uploaded'),
        ('profiled', 'Data Profiled'),
        ('analyzed', 'AI Analyzed'),
        ('transformed', 'Transformed'),
        ('completed', 'Completed'),
    ]
    
    project_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    
    original_filename = models.CharField(max_length=255, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    processed_file_path = models.CharField(max_length=500, blank=True)
    
    row_count = models.IntegerField(null=True, blank=True)
    column_count = models.IntegerField(null=True, blank=True)
    
    statistics = models.JSONField(default=dict, blank=True)
    ai_recommendations = models.JSONField(default=list, blank=True)
    applied_transformations = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['project_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.email}"