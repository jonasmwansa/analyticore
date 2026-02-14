from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

@shared_task
def cleanup_old_exports():
    """Clean up export files older than 7 days"""
    exports_path = settings.PIPELINE_STORAGE_PATH / 'exports'
    cutoff_date = timezone.now() - timedelta(days=7)
    
    deleted_count = 0
    
    try:
        for filename in os.listdir(exports_path):
            filepath = exports_path / filename
            if os.path.isfile(filepath):
                file_mtime = timezone.datetime.fromtimestamp(
                    os.path.getmtime(filepath),
                    tz=timezone.utc
                )
                if file_mtime < cutoff_date:
                    os.remove(filepath)
                    deleted_count += 1
                    logger.info(f"Deleted old export: {filename}")
    except Exception as e:
        logger.error(f"Export cleanup failed: {str(e)}")
    
    logger.info(f"Export cleanup completed: {deleted_count} files deleted")
    return deleted_count

@shared_task
def generate_export_async(project_id, export_format, user_id):
    """Generate export file asynchronously"""
    from projects.models import Project
    from users.models import User
    from users.notification_service import NotificationService
    import pandas as pd
    
    try:
        project = Project.objects.get(project_id=project_id)
        user = User.objects.get(id=user_id)
        
        # Load data
        if project.processed_file_path and os.path.exists(project.processed_file_path):
            file_path = project.processed_file_path
        elif project.file_path and os.path.exists(project.file_path):
            file_path = project.file_path
        else:
            raise ValueError("No data file available")
        
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_json(file_path)
        
        # Generate export
        exports_path = settings.PIPELINE_STORAGE_PATH / 'exports'
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        
        if export_format == 'csv':
            export_filename = f"{project.project_id}_{timestamp}.csv"
            export_path = exports_path / export_filename
            df.to_csv(export_path, index=False)
        elif export_format == 'excel':
            export_filename = f"{project.project_id}_{timestamp}.xlsx"
            export_path = exports_path / export_filename
            df.to_excel(export_path, index=False)
        elif export_format == 'json':
            export_filename = f"{project.project_id}_{timestamp}.json"
            export_path = exports_path / export_filename
            df.to_json(export_path, orient='records')
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        # Send notification
        NotificationService.create_notification(
            user=user,
            notification_type='export_ready',
            title='Export Ready',
            message=f'Your {export_format.upper()} export for "{project.name}" is ready to download.',
            related_project_id=project.project_id,
            send_email=True,
            send_push=True,
        )
        
        logger.info(f"Export generated: {export_filename}")
        return str(export_path)
        
    except Exception as e:
        logger.error(f"Export generation failed: {str(e)}")
        raise
