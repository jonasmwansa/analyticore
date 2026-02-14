"""
Comprehensive Backend Tests for AnalytiCore Analysis API
Tests: Statistics, Correlation, Distribution, Chart Data, Columns APIs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from main agent context
ADMIN_EMAIL = "admin@analyticore.com"
ADMIN_PASSWORD = "adminpassword"
TEST_PROJECT_ID = "7085cebf-46de-4266-9a80-274b5c3bc425"


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


class TestStatisticsAPI:
    """Statistics API endpoint tests - GET /api/analysis/{id}/statistics"""
    
    def test_statistics_returns_200(self, auth_token):
        """Test statistics endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/statistics",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200, f"Statistics API failed: {response.status_code}"
        print("Statistics API returned 200")
        
    def test_statistics_has_numeric_data(self, auth_token):
        """Test statistics contains numeric column stats"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/statistics",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        data = response.json()
        
        # Verify structure
        assert "numeric" in data, "Missing numeric section"
        assert "categorical" in data, "Missing categorical section"
        assert "summary" in data, "Missing summary section"
        
        # Verify numeric columns have required metrics
        numeric = data["numeric"]
        assert len(numeric) > 0, "No numeric columns found"
        
        for col_name, stats in numeric.items():
            assert "count" in stats, f"Missing count for {col_name}"
            assert "mean" in stats, f"Missing mean for {col_name}"
            assert "std" in stats, f"Missing std for {col_name}"
            assert "min" in stats, f"Missing min for {col_name}"
            assert "25%" in stats, f"Missing 25% for {col_name}"
            assert "50%" in stats, f"Missing 50%/median for {col_name}"
            assert "75%" in stats, f"Missing 75% for {col_name}"
            assert "max" in stats, f"Missing max for {col_name}"
            print(f"Verified stats for numeric column: {col_name}")
            
    def test_statistics_summary_metrics(self, auth_token):
        """Test summary contains overall dataset metrics"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/statistics",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        summary = response.json()["summary"]
        
        assert "total_rows" in summary and summary["total_rows"] > 0
        assert "total_columns" in summary and summary["total_columns"] > 0
        assert "numeric_columns" in summary
        assert "total_missing" in summary
        assert "total_duplicates" in summary
        print(f"Summary: {summary['total_rows']} rows, {summary['total_columns']} columns")
        
    def test_statistics_requires_auth(self):
        """Test statistics endpoint requires authentication"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/statistics",
            timeout=10
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Statistics API properly secured")


class TestCorrelationAPI:
    """Correlation API endpoint tests - GET /api/analysis/{id}/correlation"""
    
    def test_correlation_returns_200(self, auth_token):
        """Test correlation endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/correlation",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200, f"Correlation API failed: {response.status_code}"
        print("Correlation API returned 200")
        
    def test_correlation_matrix_structure(self, auth_token):
        """Test correlation returns proper matrix structure"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/correlation",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        data = response.json()
        
        assert "matrix" in data, "Missing correlation matrix"
        assert "columns" in data, "Missing columns list"
        assert "method" in data, "Missing method"
        assert "heatmap_data" in data, "Missing heatmap data"
        
        # Verify heatmap data format
        if data["heatmap_data"]:
            for cell in data["heatmap_data"]:
                assert "x" in cell, "Missing x in heatmap cell"
                assert "y" in cell, "Missing y in heatmap cell"
                assert "value" in cell, "Missing value in heatmap cell"
        print(f"Correlation matrix has {len(data['columns'])} numeric columns")
        
    def test_correlation_top_correlations(self, auth_token):
        """Test correlation returns top correlations"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/correlation",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        data = response.json()
        
        assert "top_correlations" in data, "Missing top correlations"
        
        if data["top_correlations"]:
            for corr in data["top_correlations"]:
                assert "column1" in corr
                assert "column2" in corr
                assert "correlation" in corr
                assert "strength" in corr
                assert -1 <= corr["correlation"] <= 1, f"Invalid correlation value: {corr['correlation']}"
        print(f"Found {len(data.get('top_correlations', []))} top correlations")
        
    def test_correlation_with_method_param(self, auth_token):
        """Test correlation with different methods"""
        for method in ["pearson", "spearman", "kendall"]:
            response = requests.get(
                f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/correlation?method={method}",
                headers={"Authorization": f"Token {auth_token}"},
                timeout=10
            )
            assert response.status_code == 200, f"Correlation with {method} failed"
            assert response.json()["method"] == method
            print(f"Correlation with method={method} works")


class TestDistributionAPI:
    """Distribution API endpoint tests - GET /api/analysis/{id}/distribution"""
    
    def test_distribution_returns_200(self, auth_token):
        """Test distribution endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/distribution",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200, f"Distribution API failed: {response.status_code}"
        print("Distribution API returned 200")
        
    def test_distribution_for_specific_column(self, auth_token):
        """Test distribution for specific column"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/distribution?column=age",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        data = response.json()
        
        assert "distributions" in data
        assert "age" in data["distributions"]
        
        age_dist = data["distributions"]["age"]
        assert "histogram" in age_dist, "Missing histogram data"
        assert "box_plot" in age_dist, "Missing box plot data"
        assert "normality_tests" in age_dist, "Missing normality tests"
        assert "skewness" in age_dist, "Missing skewness"
        assert "kurtosis" in age_dist, "Missing kurtosis"
        print("Distribution for age column has all required fields")
        
    def test_distribution_histogram_structure(self, auth_token):
        """Test histogram data structure"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/distribution?column=salary&bins=20",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        histogram = response.json()["distributions"]["salary"]["histogram"]
        
        assert len(histogram) > 0, "Histogram is empty"
        
        for bin_data in histogram:
            assert "bin_start" in bin_data
            assert "bin_end" in bin_data
            assert "count" in bin_data
            assert "bin_center" in bin_data
        print(f"Histogram has {len(histogram)} bins")
        
    def test_distribution_box_plot_data(self, auth_token):
        """Test box plot statistics"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/distribution?column=age",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        box_plot = response.json()["distributions"]["age"]["box_plot"]
        
        required_fields = ["min", "q1", "median", "q3", "max", "whisker_low", "whisker_high", "iqr"]
        for field in required_fields:
            assert field in box_plot, f"Missing {field} in box plot"
        
        # Verify ordering
        assert box_plot["min"] <= box_plot["q1"] <= box_plot["median"] <= box_plot["q3"] <= box_plot["max"]
        print("Box plot data validated")
        
    def test_distribution_normality_tests(self, auth_token):
        """Test normality test results"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/distribution?column=age",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        normality = response.json()["distributions"]["age"]["normality_tests"]
        
        if "shapiro" in normality:
            assert "statistic" in normality["shapiro"]
            assert "p_value" in normality["shapiro"]
            assert "is_normal" in normality["shapiro"]
            print(f"Shapiro test: is_normal={normality['shapiro']['is_normal']}")


class TestChartDataAPI:
    """Chart Data API endpoint tests - GET /api/analysis/{id}/chart"""
    
    def test_scatter_chart(self, auth_token):
        """Test scatter chart data generation"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/chart?type=scatter&x=age&y=salary",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["type"] == "scatter"
        assert data["x_column"] == "age"
        assert data["y_column"] == "salary"
        assert len(data["data"]) > 0
        
        for point in data["data"]:
            assert "x" in point and "y" in point
        print(f"Scatter chart has {len(data['data'])} data points")
        
    def test_line_chart(self, auth_token):
        """Test line chart data generation"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/chart?type=line&x=age&y=salary",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["type"] == "line"
        assert len(data["data"]) > 0
        print(f"Line chart has {len(data['data'])} data points")
        
    def test_bar_chart(self, auth_token):
        """Test bar chart data generation"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/chart?type=bar&x=department&y=salary",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["type"] == "bar"
        assert len(data["data"]) > 0
        
        for bar in data["data"]:
            assert "x" in bar and "y" in bar
        print(f"Bar chart has {len(data['data'])} categories")
        
    def test_pie_chart(self, auth_token):
        """Test pie chart data generation"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/chart?type=pie&x=department",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["type"] == "pie"
        assert len(data["data"]) > 0
        
        total_percentage = sum(item["percentage"] for item in data["data"])
        assert 99 <= total_percentage <= 101, f"Percentages don't sum to 100: {total_percentage}"
        print(f"Pie chart has {len(data['data'])} slices")
        
    def test_histogram_chart(self, auth_token):
        """Test histogram chart data generation"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/chart?type=histogram&x=salary",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["type"] == "histogram"
        assert len(data["data"]) > 0
        
        for bin_data in data["data"]:
            assert "count" in bin_data
        print(f"Histogram has {len(data['data'])} bins")
        
    def test_box_chart(self, auth_token):
        """Test box plot chart data generation"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/chart?type=box&y=salary",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["type"] == "box"
        assert len(data["data"]) > 0
        
        for box in data["data"]:
            assert "min" in box
            assert "q1" in box
            assert "median" in box
            assert "q3" in box
            assert "max" in box
        print(f"Box chart has {len(data['data'])} boxes")
        
    def test_heatmap_chart(self, auth_token):
        """Test heatmap chart data generation"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/chart?type=heatmap",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["type"] == "heatmap"
        assert len(data["data"]) > 0
        print(f"Heatmap has {len(data['data'])} cells")


class TestColumnsAPI:
    """Columns API endpoint tests - GET /api/analysis/{id}/columns"""
    
    def test_columns_returns_200(self, auth_token):
        """Test columns endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/columns",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200
        print("Columns API returned 200")
        
    def test_columns_structure(self, auth_token):
        """Test columns response structure"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/columns",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        data = response.json()
        
        assert "columns" in data
        assert "numeric" in data
        assert "categorical" in data
        assert "datetime" in data
        
        for col in data["columns"]:
            assert "name" in col
            assert "type" in col
            assert "dtype" in col
        print(f"Found {len(data['columns'])} columns total")


class TestDataPreviewAPI:
    """Data Preview API endpoint tests - GET /api/projects/{id}/data"""
    
    def test_data_preview_returns_200(self, auth_token):
        """Test data preview endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/data",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        assert response.status_code == 200
        print("Data preview API returned 200")
        
    def test_data_preview_structure(self, auth_token):
        """Test data preview response structure"""
        response = requests.get(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/data",
            headers={"Authorization": f"Token {auth_token}"},
            timeout=10
        )
        data = response.json()
        
        assert "data" in data, "Missing data array"
        assert "total_rows" in data, "Missing total_rows"
        assert "columns" in data, "Missing columns"
        
        assert len(data["data"]) > 0, "Data array is empty"
        assert data["total_rows"] > 0, "Total rows should be > 0"
        print(f"Data preview: {data['total_rows']} rows, {len(data['columns'])} columns")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
