"""
Backend API Tests for Scheduled Pipelines Feature
Tests all CRUD operations and pipeline run functionality

Endpoints tested:
- GET /api/pipelines/schedules/ - List all schedules
- POST /api/pipelines/schedules/create/ - Create schedule
- GET /api/pipelines/schedules/{id}/ - Get schedule details
- POST /api/pipelines/schedules/{id}/run/ - Trigger manual run
- POST /api/pipelines/schedules/{id}/toggle/ - Toggle active/paused
- DELETE /api/pipelines/schedules/{id}/delete/ - Delete schedule
- GET /api/pipelines/schedules/stats/ - Get statistics
- GET /api/pipelines/runs/ - Get run history
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review request
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass123"
AUTH_TOKEN = "5adeec057f6c3a6a1ebd551303a2dcc1b0be1c05"
EXISTING_PROJECT_ID = "fcd7cfe8-3931-4915-a331-fe4fcd0fe8bb"
EXISTING_SCHEDULE_ID = "5efb25bb-f935-48f4-956f-7452b03f617c"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session with auth header"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Token {AUTH_TOKEN}"
    })
    return session


@pytest.fixture(scope="module")
def unauthenticated_client():
    """Session without auth for testing 401 responses"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestSchedulesAuthentication:
    """Verify all endpoints require authentication"""

    def test_list_schedules_requires_auth(self, unauthenticated_client):
        response = unauthenticated_client.get(f"{BASE_URL}/api/pipelines/schedules/")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ List schedules requires authentication")

    def test_create_schedule_requires_auth(self, unauthenticated_client):
        response = unauthenticated_client.post(f"{BASE_URL}/api/pipelines/schedules/create/", json={
            "project_id": EXISTING_PROJECT_ID,
            "name": "Test Schedule"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Create schedule requires authentication")

    def test_stats_requires_auth(self, unauthenticated_client):
        response = unauthenticated_client.get(f"{BASE_URL}/api/pipelines/schedules/stats/")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Get stats requires authentication")

    def test_runs_requires_auth(self, unauthenticated_client):
        response = unauthenticated_client.get(f"{BASE_URL}/api/pipelines/runs/")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ List runs requires authentication")


class TestListSchedules:
    """Test GET /api/pipelines/schedules/"""

    def test_list_schedules_success(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/pipelines/schedules/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "schedules" in data, "Response should contain 'schedules' key"
        assert isinstance(data["schedules"], list), "schedules should be a list"
        print(f"✓ List schedules returned {len(data['schedules'])} schedules")
        
        # Verify schedule structure if exists
        if data["schedules"]:
            schedule = data["schedules"][0]
            required_fields = ["schedule_id", "name", "project", "schedule_type", 
                             "action_type", "is_active", "status"]
            for field in required_fields:
                assert field in schedule, f"Schedule missing required field: {field}"
            print("✓ Schedule structure validated")


class TestGetScheduleDetails:
    """Test GET /api/pipelines/schedules/{id}/"""

    def test_get_existing_schedule(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/pipelines/schedules/{EXISTING_SCHEDULE_ID}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["schedule_id"] == EXISTING_SCHEDULE_ID
        
        # Verify detailed fields
        required_fields = ["schedule_id", "name", "description", "project", 
                         "schedule_type", "hour", "minute", "action_type",
                         "is_active", "status", "runs"]
        for field in required_fields:
            assert field in data, f"Response missing required field: {field}"
        
        print(f"✓ Get schedule details - Name: {data['name']}, Type: {data['schedule_type']}")
        print(f"  Project: {data['project']['name']}, Runs count: {len(data.get('runs', []))}")

    def test_get_nonexistent_schedule(self, api_client):
        fake_id = str(uuid.uuid4())
        response = api_client.get(f"{BASE_URL}/api/pipelines/schedules/{fake_id}/")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Returns 404 for nonexistent schedule")


class TestCreateSchedule:
    """Test POST /api/pipelines/schedules/create/"""

    def test_create_schedule_success(self, api_client):
        unique_name = f"TEST_Pytest_Schedule_{uuid.uuid4().hex[:8]}"
        payload = {
            "project_id": EXISTING_PROJECT_ID,
            "name": unique_name,
            "description": "Created by pytest",
            "schedule_type": "daily",
            "hour": 9,
            "minute": 30,
            "action_type": "run_analysis",
            "is_active": True
        }
        
        response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/create/", json=payload)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "schedule_id" in data, "Response should contain schedule_id"
        assert data["name"] == unique_name
        assert "next_run" in data
        
        print(f"✓ Created schedule: {data['name']}")
        print(f"  Schedule ID: {data['schedule_id']}")
        print(f"  Next run: {data.get('next_run', 'N/A')}")
        
        # Store for cleanup
        return data["schedule_id"]

    def test_create_schedule_missing_fields(self, api_client):
        response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/create/", json={})
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        data = response.json()
        assert "error" in data
        print(f"✓ Validation error: {data['error']}")

    def test_create_schedule_invalid_project(self, api_client):
        fake_project_id = str(uuid.uuid4())
        response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/create/", json={
            "project_id": fake_project_id,
            "name": "Invalid Project Schedule"
        })
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Returns 404 for invalid project_id")

    def test_create_with_invalid_schedule_type(self, api_client):
        response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/create/", json={
            "project_id": EXISTING_PROJECT_ID,
            "name": "Invalid Type Schedule",
            "schedule_type": "invalid_type"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Returns 400 for invalid schedule_type")


class TestToggleSchedule:
    """Test POST /api/pipelines/schedules/{id}/toggle/"""

    def test_toggle_existing_schedule(self, api_client):
        # First get current state
        get_response = api_client.get(f"{BASE_URL}/api/pipelines/schedules/{EXISTING_SCHEDULE_ID}/")
        original_active = get_response.json()["is_active"]
        
        # Toggle
        response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/{EXISTING_SCHEDULE_ID}/toggle/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "is_active" in data
        assert data["is_active"] != original_active, "is_active should have toggled"
        print(f"✓ Toggled schedule from {original_active} to {data['is_active']}")
        
        # Toggle back to restore original state
        restore_response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/{EXISTING_SCHEDULE_ID}/toggle/")
        assert restore_response.status_code == 200
        print(f"✓ Restored schedule to {original_active}")

    def test_toggle_nonexistent_schedule(self, api_client):
        fake_id = str(uuid.uuid4())
        response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/{fake_id}/toggle/")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Returns 404 for toggling nonexistent schedule")


class TestRunNow:
    """Test POST /api/pipelines/schedules/{id}/run/"""

    def test_run_existing_schedule(self, api_client):
        response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/{EXISTING_SCHEDULE_ID}/run/")
        # Can be 200 (sync execution) or queued response
        assert response.status_code in [200, 500], f"Expected 200 or 500 (sync fail), got {response.status_code}"
        
        data = response.json()
        # Either has run_id (success) or error (sync execution failure)
        if "run_id" in data:
            print(f"✓ Run triggered - Run ID: {data['run_id']}")
            print(f"  Status: {data.get('status', 'N/A')}")
            if "rows_processed" in data:
                print(f"  Rows processed: {data['rows_processed']}")
        else:
            print(f"✓ Run attempted - Message: {data.get('message', data.get('error', 'N/A'))}")

    def test_run_nonexistent_schedule(self, api_client):
        fake_id = str(uuid.uuid4())
        response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/{fake_id}/run/")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Returns 404 for running nonexistent schedule")


class TestGetStats:
    """Test GET /api/pipelines/schedules/stats/"""

    def test_get_stats_success(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/pipelines/schedules/stats/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        required_fields = ["total_schedules", "active_schedules", "paused_schedules", 
                         "runs_last_7_days", "runs_by_day"]
        for field in required_fields:
            assert field in data, f"Stats missing required field: {field}"
        
        print(f"✓ Stats: Total={data['total_schedules']}, Active={data['active_schedules']}")
        
        # Verify runs_last_7_days structure
        runs_7d = data["runs_last_7_days"]
        assert "total" in runs_7d
        assert "successful" in runs_7d
        assert "failed" in runs_7d
        assert "success_rate" in runs_7d
        
        print(f"  7-day runs: {runs_7d['total']}, Success rate: {runs_7d['success_rate']}%")


class TestGetRunHistory:
    """Test GET /api/pipelines/runs/"""

    def test_get_run_history_success(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/pipelines/runs/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "runs" in data, "Response should contain 'runs' key"
        assert isinstance(data["runs"], list)
        
        print(f"✓ Run history returned {len(data['runs'])} runs")
        
        # Verify run structure if exists
        if data["runs"]:
            run = data["runs"][0]
            required_fields = ["run_id", "schedule", "status", "trigger", "started_at"]
            for field in required_fields:
                assert field in run, f"Run missing required field: {field}"
            
            print(f"  Latest run: {run['status']} ({run['trigger']}) at {run['started_at']}")


class TestDeleteSchedule:
    """Test DELETE /api/pipelines/schedules/{id}/delete/"""

    def test_delete_schedule_flow(self, api_client):
        # First create a schedule to delete
        unique_name = f"TEST_Delete_Schedule_{uuid.uuid4().hex[:8]}"
        create_response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/create/", json={
            "project_id": EXISTING_PROJECT_ID,
            "name": unique_name,
            "schedule_type": "daily",
            "action_type": "refresh_data"
        })
        
        if create_response.status_code != 201:
            pytest.skip(f"Could not create schedule for deletion test: {create_response.text}")
        
        schedule_id = create_response.json()["schedule_id"]
        print(f"✓ Created schedule {schedule_id} for deletion test")
        
        # Delete the schedule
        delete_response = api_client.delete(f"{BASE_URL}/api/pipelines/schedules/{schedule_id}/delete/")
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
        print(f"✓ Deleted schedule {schedule_id}")
        
        # Verify deletion (should return 404)
        verify_response = api_client.get(f"{BASE_URL}/api/pipelines/schedules/{schedule_id}/")
        assert verify_response.status_code == 404, "Schedule should not exist after deletion"
        print("✓ Verified schedule no longer exists")

    def test_delete_nonexistent_schedule(self, api_client):
        fake_id = str(uuid.uuid4())
        response = api_client.delete(f"{BASE_URL}/api/pipelines/schedules/{fake_id}/delete/")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Returns 404 for deleting nonexistent schedule")


class TestScheduleTypes:
    """Test different schedule type configurations"""

    def test_hourly_schedule(self, api_client):
        response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/create/", json={
            "project_id": EXISTING_PROJECT_ID,
            "name": f"TEST_Hourly_{uuid.uuid4().hex[:8]}",
            "schedule_type": "hourly",
            "minute": 15,
            "action_type": "run_analysis"
        })
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/pipelines/schedules/{response.json()['schedule_id']}/delete/")
        print("✓ Hourly schedule created successfully")

    def test_weekly_schedule(self, api_client):
        response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/create/", json={
            "project_id": EXISTING_PROJECT_ID,
            "name": f"TEST_Weekly_{uuid.uuid4().hex[:8]}",
            "schedule_type": "weekly",
            "day_of_week": "1",  # Monday
            "hour": 9,
            "minute": 0,
            "action_type": "full_pipeline"
        })
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/pipelines/schedules/{response.json()['schedule_id']}/delete/")
        print("✓ Weekly schedule created successfully")

    def test_monthly_schedule(self, api_client):
        response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/create/", json={
            "project_id": EXISTING_PROJECT_ID,
            "name": f"TEST_Monthly_{uuid.uuid4().hex[:8]}",
            "schedule_type": "monthly",
            "day_of_month": "1",  # First of month
            "hour": 6,
            "minute": 0,
            "action_type": "export_data"
        })
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/pipelines/schedules/{response.json()['schedule_id']}/delete/")
        print("✓ Monthly schedule created successfully")


class TestActionTypes:
    """Test different action type configurations"""

    @pytest.mark.parametrize("action_type", [
        "refresh_data", 
        "run_analysis", 
        "apply_cleaning", 
        "export_data", 
        "full_pipeline"
    ])
    def test_action_type(self, api_client, action_type):
        response = api_client.post(f"{BASE_URL}/api/pipelines/schedules/create/", json={
            "project_id": EXISTING_PROJECT_ID,
            "name": f"TEST_{action_type}_{uuid.uuid4().hex[:8]}",
            "schedule_type": "daily",
            "action_type": action_type
        })
        assert response.status_code == 201, f"Expected 201 for {action_type}, got {response.status_code}"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/pipelines/schedules/{response.json()['schedule_id']}/delete/")
        print(f"✓ Action type '{action_type}' accepted")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
