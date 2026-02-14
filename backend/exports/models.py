from django.db import models
from projects.models import Project
import uuid

class Export(models.Model):
    EXPORT_TYPES = [
        ('csv', 'CSV File'),
        ('excel', 'Excel File'),
        ('json', 'JSON File'),
        ('pdf_report', 'PDF Report'),
        ('chart_png', 'Chart PNG'),
        ('chart_html', 'Interactive Chart HTML'),
    ]
    
    export_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='exports')
    export_type = models.CharField(max_length=20, choices=EXPORT_TYPES)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exports'
        ordering = ['-created_at']