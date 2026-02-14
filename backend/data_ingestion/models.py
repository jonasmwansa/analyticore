from django.db import models
from django.conf import settings
import uuid

class DataSource(models.Model):
    SOURCE_TYPES = [
        ('file', 'File Upload'),
        ('mysql', 'MySQL Database'),
        ('postgresql', 'PostgreSQL Database'),
        ('api', 'REST API'),
        ('csv_url', 'CSV URL'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='data_sources')
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    
    connection_details = models.JSONField(default=dict, help_text="Encrypted connection details")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_sources'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'source_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"

class DataUpload(models.Model):
    UPLOAD_STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cleaned', 'Cleaned'),
        ('transformed', 'Transformed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='data_uploads')
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='uploads')

    original_file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)

    has_header = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=UPLOAD_STATUS_CHOICES,
        default='uploaded'
    )

    columns = models.JSONField(null=True, blank=True)
    row_count = models.PositiveIntegerField(null=True, blank=True)
    preview_data = models.JSONField(null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    cleaned_file = models.FileField(upload_to='cleaned/%Y/%m/%d/', null=True, blank=True)
    cleaning_rules = models.JSONField(null=True, blank=True)
    cleaning_stats = models.JSONField(null=True, blank=True)
    cleaned_at = models.DateTimeField(null=True, blank=True)
    is_cleaned_version = models.BooleanField(default=False)
    original_upload = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cleaned_versions'
    )

    class Meta:
        db_table = 'data_uploads'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['uploaded_at']),
        ]

    def __str__(self):
        return f"{self.file_name} ({self.get_status_display()})"
