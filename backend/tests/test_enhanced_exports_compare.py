"""
Tests for Enhanced Export APIs and Compare Projects APIs
- Summary Statistics Export (CSV/Excel)
- Correlation Matrix Export (CSV/Excel with different methods)
- Distribution Analysis Export (CSV/Excel)
- Visualization Export (PNG/SVG for correlation, distribution, summary)
- Comparable Projects List
- Compare Projects
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthSetup:
    """Authentication setup for tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@analyticore.com",
            "password": "adminpassword"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Token {auth_token}",
            "Content-Type": "application/json"
        }
    
    @pytest.fixture(scope="class")
    def project_id(self):
        """Return test project ID"""
        return "590b784e-be98-439f-b41c-770c5a1ab704"


class TestEnhancedExportStatistics(TestAuthSetup):
    """Tests for export-statistics endpoint"""
    
    def test_export_statistics_csv(self, auth_headers, project_id):
        """Test export summary statistics as CSV"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-statistics?export_format=csv",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "filename" in data
        assert "content_type" in data
        assert "content" in data
        assert data["content_type"] == "text/csv"
        assert ".csv" in data["filename"]
        assert "SUMMARY STATISTICS" in data["content"]
        assert "NUMERIC COLUMNS" in data["content"]
        print(f"SUCCESS: Statistics CSV export - filename: {data['filename']}")
    
    def test_export_statistics_excel(self, auth_headers, project_id):
        """Test export summary statistics as Excel"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-statistics?export_format=excel",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "filename" in data
        assert "content_type" in data
        assert "content" in data
        assert "encoding" in data
        assert data["content_type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert data["encoding"] == "base64"
        assert ".xlsx" in data["filename"]
        print(f"SUCCESS: Statistics Excel export - filename: {data['filename']}")


class TestEnhancedExportCorrelation(TestAuthSetup):
    """Tests for export-correlation endpoint"""
    
    def test_export_correlation_csv_pearson(self, auth_headers, project_id):
        """Test export correlation matrix as CSV with Pearson method"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-correlation?export_format=csv&method=pearson",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "filename" in data
        assert "content_type" in data
        assert "content" in data
        assert data["content_type"] == "text/csv"
        assert "pearson" in data["filename"].lower()
        assert "# Correlation Matrix" in data["content"]
        assert "Top Correlations" in data["content"]
        print(f"SUCCESS: Correlation CSV (Pearson) - filename: {data['filename']}")
    
    def test_export_correlation_csv_spearman(self, auth_headers, project_id):
        """Test export correlation matrix as CSV with Spearman method"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-correlation?export_format=csv&method=spearman",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["content_type"] == "text/csv"
        assert "spearman" in data["filename"].lower()
        print(f"SUCCESS: Correlation CSV (Spearman) - filename: {data['filename']}")
    
    def test_export_correlation_csv_kendall(self, auth_headers, project_id):
        """Test export correlation matrix as CSV with Kendall method"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-correlation?export_format=csv&method=kendall",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["content_type"] == "text/csv"
        assert "kendall" in data["filename"].lower()
        print(f"SUCCESS: Correlation CSV (Kendall) - filename: {data['filename']}")
    
    def test_export_correlation_excel(self, auth_headers, project_id):
        """Test export correlation matrix as Excel"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-correlation?export_format=excel&method=pearson",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["content_type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert data["encoding"] == "base64"
        assert ".xlsx" in data["filename"]
        print(f"SUCCESS: Correlation Excel - filename: {data['filename']}")


class TestEnhancedExportDistribution(TestAuthSetup):
    """Tests for export-distribution endpoint"""
    
    def test_export_distribution_csv(self, auth_headers, project_id):
        """Test export distribution analysis as CSV"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-distribution?export_format=csv",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "filename" in data
        assert "content_type" in data
        assert "content" in data
        assert data["content_type"] == "text/csv"
        assert "# Distribution Analysis" in data["content"]
        assert "Box Plot Statistics" in data["content"]
        assert "Histogram" in data["content"]
        print(f"SUCCESS: Distribution CSV - filename: {data['filename']}")
    
    def test_export_distribution_excel(self, auth_headers, project_id):
        """Test export distribution analysis as Excel"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-distribution?export_format=excel",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["content_type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert data["encoding"] == "base64"
        print(f"SUCCESS: Distribution Excel - filename: {data['filename']}")


class TestEnhancedExportVisualization(TestAuthSetup):
    """Tests for export-visualization endpoint"""
    
    def test_export_visualization_correlation_png(self, auth_headers, project_id):
        """Test export correlation heatmap as PNG"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-visualization?export_format=png&chart_type=correlation",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "filename" in data
        assert "content_type" in data
        assert "content" in data
        assert data["content_type"] == "image/png"
        assert data["encoding"] == "base64"
        assert ".png" in data["filename"]
        assert "correlation" in data["filename"].lower()
        print(f"SUCCESS: Visualization PNG (correlation) - filename: {data['filename']}")
    
    def test_export_visualization_correlation_svg(self, auth_headers, project_id):
        """Test export correlation heatmap as SVG"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-visualization?export_format=svg&chart_type=correlation",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["content_type"] == "image/svg+xml"
        assert data["encoding"] == "base64"
        assert ".svg" in data["filename"]
        print(f"SUCCESS: Visualization SVG (correlation) - filename: {data['filename']}")
    
    def test_export_visualization_distribution_png(self, auth_headers, project_id):
        """Test export distribution chart as PNG"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-visualization?export_format=png&chart_type=distribution",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["content_type"] == "image/png"
        assert data["encoding"] == "base64"
        assert "distribution" in data["filename"].lower()
        print(f"SUCCESS: Visualization PNG (distribution) - filename: {data['filename']}")
    
    def test_export_visualization_summary_png(self, auth_headers, project_id):
        """Test export summary dashboard as PNG"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-visualization?export_format=png&chart_type=summary",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["content_type"] == "image/png"
        assert data["encoding"] == "base64"
        assert "summary" in data["filename"].lower()
        print(f"SUCCESS: Visualization PNG (summary) - filename: {data['filename']}")
    
    def test_export_visualization_invalid_chart_type(self, auth_headers, project_id):
        """Test export visualization with invalid chart type"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-visualization?export_format=png&chart_type=invalid",
            headers=auth_headers
        )
        assert response.status_code == 400
        print("SUCCESS: Invalid chart type returns 400")


class TestCompareProjectsAPI(TestAuthSetup):
    """Tests for Compare Projects APIs"""
    
    def test_get_comparable_projects(self, auth_headers):
        """Test get list of comparable projects"""
        response = requests.get(
            f"{BASE_URL}/api/projects/comparable/",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "projects" in data
        assert isinstance(data["projects"], list)
        
        # Each project should have required fields
        if len(data["projects"]) > 0:
            project = data["projects"][0]
            assert "project_id" in project
            assert "name" in project
            assert "created_at" in project
            assert "status" in project
        
        print(f"SUCCESS: Comparable projects returned {len(data['projects'])} projects")
    
    def test_compare_projects_requires_two(self, auth_headers, project_id):
        """Test compare projects requires at least 2 projects"""
        response = requests.post(
            f"{BASE_URL}/api/projects/compare/",
            headers=auth_headers,
            json={"project_ids": [project_id]}
        )
        assert response.status_code == 400
        assert "At least 2 projects" in response.json().get("detail", "")
        print("SUCCESS: Compare requires 2+ projects validation works")
    
    def test_compare_projects_max_four(self, auth_headers, project_id):
        """Test compare projects max 4 projects"""
        fake_ids = [
            project_id, 
            "00000000-0000-0000-0000-000000000001",
            "00000000-0000-0000-0000-000000000002",
            "00000000-0000-0000-0000-000000000003",
            "00000000-0000-0000-0000-000000000004"
        ]
        response = requests.post(
            f"{BASE_URL}/api/projects/compare/",
            headers=auth_headers,
            json={"project_ids": fake_ids}
        )
        assert response.status_code == 400
        assert "Maximum 4 projects" in response.json().get("detail", "")
        print("SUCCESS: Compare max 4 projects validation works")
    
    def test_compare_projects_success(self, auth_headers):
        """Test successful comparison of 2 projects"""
        # First get comparable projects
        response = requests.get(
            f"{BASE_URL}/api/projects/comparable/",
            headers=auth_headers
        )
        projects = response.json().get("projects", [])
        
        if len(projects) < 2:
            pytest.skip("Not enough projects for comparison test")
        
        project_ids = [p["project_id"] for p in projects[:2]]
        
        response = requests.post(
            f"{BASE_URL}/api/projects/compare/",
            headers=auth_headers,
            json={"project_ids": project_ids}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "projects" in data
        assert "comparison_metrics" in data
        assert "radar_data" in data
        assert "bar_chart_data" in data
        
        assert len(data["projects"]) == 2
        
        # Check comparison metrics
        metrics = data["comparison_metrics"]
        assert "best_quality" in metrics
        assert "most_rows" in metrics
        assert "most_columns" in metrics
        assert "fewest_issues" in metrics
        assert "avg_quality_score" in metrics
        
        # Check bar chart data
        bar_data = data["bar_chart_data"]
        assert "rows" in bar_data
        assert "columns" in bar_data
        assert "quality" in bar_data
        
        print(f"SUCCESS: Compare projects returned data for {len(data['projects'])} projects")
        print(f"  - Best quality: {metrics['best_quality']}")
        print(f"  - Avg quality score: {metrics['avg_quality_score']}")


class TestExportErrorHandling(TestAuthSetup):
    """Tests for error handling in export APIs"""
    
    def test_export_invalid_project(self, auth_headers):
        """Test export with invalid project ID"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(
            f"{BASE_URL}/api/exports/{fake_id}/export-statistics?export_format=csv",
            headers=auth_headers
        )
        assert response.status_code == 404
        print("SUCCESS: Invalid project returns 404")
    
    def test_export_invalid_format(self, auth_headers, project_id):
        """Test export with invalid format"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-statistics?export_format=pdf",
            headers=auth_headers
        )
        assert response.status_code == 400
        print("SUCCESS: Invalid format returns 400")
    
    def test_export_unauthenticated(self, project_id):
        """Test export without authentication"""
        response = requests.get(
            f"{BASE_URL}/api/exports/{project_id}/export-statistics?export_format=csv"
        )
        assert response.status_code == 401
        print("SUCCESS: Unauthenticated returns 401")
