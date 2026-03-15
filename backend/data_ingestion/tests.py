from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import Project
from users.models import User


class UploadAutomationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='automation@example.com',
            password='password123',
            name='Automation User',
            is_verified=True,
        )
        self.client.force_authenticate(self.user)
        self.project = Project.objects.create(
            user=self.user,
            name='Automation Project',
            source_type='file_upload',
        )

    def test_upload_runs_automated_pipeline_and_records_stage_history(self):
        csv_content = (
            b"id,name,amount,category\n"
            b"1,Alice,10.5, retail \n"
            b"2,,12.0,retail\n"
            b"2,,12.0,retail\n"
            b"3,Bob,,services\n"
            b"4,Carla,15.5,\n"
        )

        with TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            for folder in ['original', 'processed', 'exports', 'logs', 'backups']:
                (base_path / folder).mkdir(parents=True, exist_ok=True)

            upload = SimpleUploadedFile('automation.csv', csv_content, content_type='text/csv')

            with self.settings(PIPELINE_STORAGE_PATH=base_path):
                response = self.client.post(
                    f'/api/projects/{self.project.project_id}/upload',
                    {'file': upload},
                    format='multipart',
                )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.project.refresh_from_db()
        automation = self.project.statistics.get('automation', {})
        stage_keys = [stage['key'] for stage in automation.get('stages', [])]

        self.assertEqual(self.project.status, 'completed')
        self.assertGreater(len(self.project.ai_recommendations), 0)
        self.assertEqual(stage_keys, ['cleaning', 'transformation', 'analysis', 'visualization', 'summary'])
        self.assertEqual(automation.get('status'), 'completed')
        self.assertTrue(automation.get('final_summary', {}).get('report_markdown'))
        self.assertGreaterEqual(len(self.project.applied_transformations), 1)
        self.assertTrue(self.project.processed_file_path)
        self.assertEqual(response.data['automation']['status'], 'completed')
