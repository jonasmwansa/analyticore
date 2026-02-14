"""
Test suite for Admin Analytics Dashboard APIs
Tests all analytics endpoints for the enhanced admin dashboard
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAdminAnalyticsAPI:
    """Admin Analytics API tests - requires admin credentials"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@analyticore.com",
            "password": "adminpassword"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Token {self.token}"}
    
    # === Summary Endpoint ===
    def test_analytics_summary_returns_200(self):
        """Summary endpoint returns 200 with valid data"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/summary", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "projects" in data
        assert "pipelines" in data
        assert "subscriptions" in data
    
    def test_analytics_summary_user_fields(self):
        """Summary contains user fields: total, new_today, active_today"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/summary", headers=self.headers)
        data = response.json()
        users = data["users"]
        assert "total" in users
        assert "new_today" in users
        assert "active_today" in users
        assert isinstance(users["total"], int)
    
    def test_analytics_summary_project_fields(self):
        """Summary contains project fields: total, new_today, total_rows"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/summary", headers=self.headers)
        data = response.json()
        projects = data["projects"]
        assert "total" in projects
        assert "new_today" in projects
        assert "total_rows" in projects
    
    def test_analytics_summary_pipeline_fields(self):
        """Summary contains pipeline fields: runs_today, successful, failed"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/summary", headers=self.headers)
        data = response.json()
        pipelines = data["pipelines"]
        assert "runs_today" in pipelines
        assert "successful" in pipelines
        assert "failed" in pipelines
    
    # === User Metrics Endpoint ===
    def test_user_metrics_returns_200(self):
        """User metrics endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/users", headers=self.headers)
        assert response.status_code == 200
    
    def test_user_metrics_contains_dau_wau_mau(self):
        """User metrics contains DAU, WAU, MAU"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/users", headers=self.headers)
        data = response.json()
        assert "dau" in data
        assert "wau" in data
        assert "mau" in data
        assert isinstance(data["dau"], int)
    
    def test_user_metrics_contains_stickiness_growth_churn(self):
        """User metrics contains stickiness, growth_rate, churned_users"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/users", headers=self.headers)
        data = response.json()
        assert "stickiness" in data
        assert "growth_rate" in data
        assert "churned_users" in data
        assert "returning_users" in data
    
    def test_user_metrics_verification_rate(self):
        """User metrics contains verified_users and verification_rate"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/users", headers=self.headers)
        data = response.json()
        assert "verified_users" in data
        assert "verification_rate" in data
    
    # === User Growth Endpoint ===
    def test_user_growth_returns_200(self):
        """User growth chart endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/user-growth?days=30", headers=self.headers)
        assert response.status_code == 200
    
    def test_user_growth_data_format(self):
        """User growth data has correct format"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/user-growth?days=7", headers=self.headers)
        data = response.json()
        assert "data" in data
        assert len(data["data"]) > 0
        item = data["data"][0]
        assert "date" in item
        assert "new_users" in item
        assert "total_users" in item
    
    # === System Health Endpoint ===
    def test_system_health_returns_200(self):
        """System health endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/health", headers=self.headers)
        assert response.status_code == 200
    
    def test_system_health_contains_db_metrics(self):
        """System health contains db response time and counts"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/health", headers=self.headers)
        data = response.json()
        assert "db_response_ms" in data
        assert "total_projects" in data
        assert "total_users" in data
    
    def test_system_health_contains_error_metrics(self):
        """System health contains error metrics"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/health", headers=self.headers)
        data = response.json()
        assert "errors_24h" in data
        assert "error_rate" in data
        assert "status" in data
        assert data["status"] in ["healthy", "warning", "critical"]
    
    # === Funnel Analytics Endpoint ===
    def test_funnel_analytics_returns_200(self):
        """Funnel analytics endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/funnel", headers=self.headers)
        assert response.status_code == 200
    
    def test_funnel_analytics_stages(self):
        """Funnel contains expected stages"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/funnel", headers=self.headers)
        data = response.json()
        assert "funnel" in data
        stages = [item["stage"] for item in data["funnel"]]
        assert "Signed Up" in stages
        assert "Verified Email" in stages
        assert "Created Project" in stages
    
    def test_funnel_item_format(self):
        """Funnel items have correct format"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/funnel", headers=self.headers)
        data = response.json()
        for item in data["funnel"]:
            assert "stage" in item
            assert "count" in item
            assert "rate" in item
    
    # === Project Analytics Endpoint ===
    def test_project_analytics_returns_200(self):
        """Project analytics endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/projects?days=30", headers=self.headers)
        assert response.status_code == 200
    
    def test_project_analytics_contains_totals(self):
        """Project analytics contains total fields"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/projects?days=30", headers=self.headers)
        data = response.json()
        assert "total_projects" in data
        assert "projects_this_period" in data
        assert "total_rows_processed" in data
        assert "total_analyses" in data
    
    def test_project_analytics_contains_breakdowns(self):
        """Project analytics contains status and source breakdowns"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/projects?days=30", headers=self.headers)
        data = response.json()
        assert "status_breakdown" in data
        assert "source_breakdown" in data
        assert isinstance(data["status_breakdown"], list)
        assert isinstance(data["source_breakdown"], list)
    
    # === Pipeline Analytics Endpoint ===
    def test_pipeline_analytics_returns_200(self):
        """Pipeline analytics endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/pipelines?days=30", headers=self.headers)
        assert response.status_code == 200
    
    def test_pipeline_analytics_contains_totals(self):
        """Pipeline analytics contains total fields"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/pipelines?days=30", headers=self.headers)
        data = response.json()
        assert "total_pipelines" in data
        assert "active_pipelines" in data
        assert "paused_pipelines" in data
        assert "total_runs" in data
        assert "success_rate" in data
    
    def test_pipeline_analytics_run_status(self):
        """Pipeline analytics contains run status breakdown"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/pipelines?days=30", headers=self.headers)
        data = response.json()
        assert "run_status" in data
        assert isinstance(data["run_status"], list)
    
    def test_pipeline_analytics_top_pipelines(self):
        """Pipeline analytics contains top pipelines list"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/pipelines?days=30", headers=self.headers)
        data = response.json()
        assert "top_pipelines" in data
        if len(data["top_pipelines"]) > 0:
            pipeline = data["top_pipelines"][0]
            assert "name" in pipeline
            assert "project" in pipeline
            assert "run_count" in pipeline
    
    # === Activity Analytics Endpoint ===
    def test_activity_analytics_returns_200(self):
        """Activity analytics endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/activity?days=30", headers=self.headers)
        assert response.status_code == 200
    
    def test_activity_analytics_structure(self):
        """Activity analytics has correct structure"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/activity?days=30", headers=self.headers)
        data = response.json()
        assert "top_actions" in data
        assert "resource_types" in data
        assert "daily_activity" in data
        assert "hour_distribution" in data
        assert "power_users" in data
    
    # === Retention Analytics Endpoint ===
    def test_retention_analytics_returns_200(self):
        """Retention analytics endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/retention", headers=self.headers)
        assert response.status_code == 200
    
    def test_retention_analytics_contains_retention_rates(self):
        """Retention analytics contains day retention rates"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/retention", headers=self.headers)
        data = response.json()
        assert "day1_retention" in data
        assert "day7_retention" in data
        assert "day30_retention" in data
        assert "cohort_retention" in data
    
    # === Activity Feed Endpoint ===
    def test_activity_feed_returns_200(self):
        """Activity feed endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/feed?limit=50", headers=self.headers)
        assert response.status_code == 200
    
    def test_activity_feed_structure(self):
        """Activity feed has correct structure"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/feed?limit=10", headers=self.headers)
        data = response.json()
        assert "activities" in data
        assert isinstance(data["activities"], list)
    
    # === Users List Endpoint ===
    def test_users_list_returns_200(self):
        """Users list endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/users", headers=self.headers)
        assert response.status_code == 200
    
    def test_users_list_structure(self):
        """Users list has correct structure"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/users", headers=self.headers)
        data = response.json()
        assert "users" in data
        if len(data["users"]) > 0:
            user = data["users"][0]
            assert "email" in user
            assert "project_count" in user
            assert "is_verified" in user
    
    # === Projects List Endpoint ===
    def test_projects_list_returns_200(self):
        """Projects list endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/projects", headers=self.headers)
        assert response.status_code == 200
    
    def test_projects_list_structure(self):
        """Projects list has correct structure"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/projects", headers=self.headers)
        data = response.json()
        assert "projects" in data
        if len(data["projects"]) > 0:
            project = data["projects"][0]
            assert "name" in project
            assert "user_email" in project
            assert "status" in project
            assert "source_type" in project
    
    # === Authorization Tests ===
    def test_analytics_requires_auth(self):
        """Analytics endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/summary")
        assert response.status_code == 401
    
    def test_analytics_requires_admin(self):
        """Analytics endpoints require admin (is_staff) user"""
        # Login as non-admin user
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123"
        })
        if login_resp.status_code == 200:
            token = login_resp.json()["token"]
            headers = {"Authorization": f"Token {token}"}
            response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/summary", headers=headers)
            # Non-admin should get 403 Forbidden
            assert response.status_code == 403


class TestSubscriptionAnalytics:
    """Subscription analytics tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@analyticore.com",
            "password": "adminpassword"
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Token {self.token}"}
    
    def test_subscription_analytics_returns_200(self):
        """Subscription analytics endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/subscriptions", headers=self.headers)
        assert response.status_code == 200
    
    def test_subscription_analytics_structure(self):
        """Subscription analytics has correct structure"""
        response = requests.get(f"{BASE_URL}/api/saas-admin/analytics/subscriptions", headers=self.headers)
        data = response.json()
        assert "subscription_breakdown" in data
        assert "total_subscriptions" in data
        assert "conversion_rate" in data
