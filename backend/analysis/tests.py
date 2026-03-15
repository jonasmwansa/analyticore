from pathlib import Path
from tempfile import TemporaryDirectory

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import Project
from users.models import User


class AutomationEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='analysis@example.com',
            password='password123',
            name='Analysis User',
            is_verified=True,
        )
        self.client.force_authenticate(self.user)

    def test_manual_automation_endpoint_reruns_full_pipeline(self):
        csv_content = (
            "id,value,group\n"
            "1,10,a\n"
            "2,20,a\n"
            "2,20,a\n"
            "3,,b\n"
        )

        with TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            for folder in ['original', 'processed', 'exports', 'logs', 'backups']:
                (base_path / folder).mkdir(parents=True, exist_ok=True)

            original_path = base_path / 'original' / 'manual.csv'
            original_path.write_text(csv_content, encoding='utf-8')

            project = Project.objects.create(
                user=self.user,
                name='Manual Automation Project',
                source_type='file_upload',
                status='uploaded',
                original_filename='manual.csv',
                file_path=str(original_path),
                row_count=4,
                column_count=3,
                completed_at=timezone.now(),
            )

            with self.settings(PIPELINE_STORAGE_PATH=base_path):
                response = self.client.post(f'/api/analysis/{project.project_id}/automate', {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        project.refresh_from_db()
        self.assertEqual(project.status, 'completed')
        self.assertEqual(response.data['automation']['source'], 'manual')
        self.assertEqual(len(response.data['automation']['stages']), 5)
        self.assertEqual(
            [stage['key'] for stage in response.data['automation']['stages']],
            ['cleaning', 'transformation', 'analysis', 'visualization', 'summary'],
        )
        self.assertIn('report_markdown', response.data['automation']['final_summary'])
