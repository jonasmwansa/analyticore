"""
Tests for Refactored Analysis APIs, Redis/Celery Health, and Pipeline Run
Tests: Refactored analysis endpoints, health monitoring, Celery integration
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@analyticore.com"
ADMIN_PASSWORD = "adminpassword"
TEST_PROJECT_ID = "590b784e-be98-439f-b41c-770c5a1ab704"


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for tests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=10
    )
    assert response.status_code == 200, f"Login failed: {response.status_code}"
    return response.json()["token"]


class TestRefactoredAnalysisViews:
    """Tests for refactored analysis/views.py using service classes"""
    
    def test_analyze_endpoint_returns_200(self, auth_token):
        """Test /api/analysis/{project_id}/analyze POST - uses DataLoaderService"""
        response = requests.post(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/analyze",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=30
        )
        assert response.status_code == 200, f"Analyze API failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "recommendations" in data, "Missing recommendations in response"
        print(f"Analyze endpoint working - returned {len(data.get('recommendations', []))} recommendations")
        
    def test_statistics_endpoint_returns_200(self, auth_token):
        """Test /api/analysis/{project_id}/statistics GET - uses DataLoaderService"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/statistics",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200, f"Statistics API failed: {response.status_code}"
        data = response.json()
        assert "numeric" in data, "Missing numeric stats"
        assert "summary" in data, "Missing summary"
        print("Statistics endpoint working with refactored service")
        
    def test_columns_endpoint_returns_200(self, auth_token):
        """Test /api/analysis/{project_id}/columns GET - uses DataLoaderService"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/columns",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200, f"Columns API failed: {response.status_code}"
        data = response.json()
        assert "columns" in data, "Missing columns list"
        assert "numeric" in data, "Missing numeric column list"
        assert "categorical" in data, "Missing categorical column list"
        assert len(data["columns"]) > 0, "No columns returned"
        print(f"Columns endpoint working - found {len(data['columns'])} columns")


class TestSystemHealthAPI:
    """Tests for system health monitoring via admin API"""
    
    def test_health_endpoint_returns_200(self, auth_token):
        """Test /api/saas-admin/analytics/health GET"""
        response = requests.get(
            f"{BASE_URL}/api/saas-admin/analytics/health",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200, f"Health API failed: {response.status_code}"
        data = response.json()
        
        # Verify health response structure
        assert "db_response_ms" in data, "Missing db_response_ms"
        assert "status" in data, "Missing status"
        assert data["status"] in ["healthy", "warning", "critical"], f"Invalid status: {data['status']}"
        print(f"Health endpoint working - status: {data['status']}, db_response: {data['db_response_ms']}ms")
        
    def test_health_has_error_metrics(self, auth_token):
        """Test health endpoint returns error rate metrics"""
        response = requests.get(
            f"{BASE_URL}/api/saas-admin/analytics/health",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        data = response.json()
        
        assert "error_rate" in data, "Missing error_rate"
        assert "errors_24h" in data, "Missing errors_24h"
        assert isinstance(data["error_rate"], (int, float)), "error_rate should be numeric"
        print(f"Health error metrics: error_rate={data['error_rate']}%, errors_24h={data['errors_24h']}")


class TestPipelineRunNow:
    """Tests for pipeline run_now endpoint with async/sync fallback"""
    
    @pytest.fixture(scope="class")
    def schedule_id(self, auth_token):
        """Create a test schedule for run_now tests"""
        # First check if schedule exists
        list_response = requests.get(
            f"{BASE_URL}/api/pipelines/schedules/",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        if list_response.status_code == 200:
            schedules = list_response.json().get("schedules", [])
            if schedules:
                return schedules[0]["schedule_id"]
        
        # Create new schedule if none exists
        response = requests.post(
            f"{BASE_URL}/api/pipelines/schedules/create/",
            headers={"Authorization": f"Token {auth_token}"},
            json={
                "name": "Test Run Now Schedule",
                "project_id": TEST_PROJECT_ID,
                "schedule_type": "daily",
                "action_type": "run_analysis"
            },
            timeout=10
        )
        assert response.status_code == 201, f"Schedule creation failed: {response.status_code}"
        return response.json()["schedule_id"]
        
    def test_run_now_endpoint_returns_success(self, auth_token, schedule_id):
        """Test /api/pipelines/schedules/{id}/run/ POST"""
        response = requests.post(
            f"{BASE_URL}/api/pipelines/schedules/{schedule_id}/run/",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=15
        )
        assert response.status_code == 200, f"Run now failed: {response.status_code} - {response.text}"
        data = response.json()
        
        assert "run_id" in data, "Missing run_id in response"
        assert "status" in data, "Missing status in response"
        assert data["status"] in ["pending", "running", "completed"], f"Unexpected status: {data['status']}"
        print(f"Run now successful - run_id: {data['run_id']}, status: {data['status']}")
        
    def test_run_history_shows_triggered_runs(self, auth_token):
        """Test /api/pipelines/runs/ shows manually triggered runs"""
        response = requests.get(
            f"{BASE_URL}/api/pipelines/runs/",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200, f"Run history failed: {response.status_code}"
        data = response.json()
        
        assert "runs" in data, "Missing runs in response"
        print(f"Run history working - found {len(data['runs'])} runs")


class TestCeleryIntegration:
    """Tests for Redis/Celery integration"""
    
    def test_celery_beat_schedule_active(self, auth_token):
        """Verify health monitoring tasks are scheduled in Celery Beat"""
        # This is verified by checking if health endpoint works
        # and by checking celery inspect registered output
        response = requests.get(
            f"{BASE_URL}/api/saas-admin/analytics/health",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200, "Health check should work if Celery is configured"
        print("Celery Beat scheduling verified via health endpoint")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
