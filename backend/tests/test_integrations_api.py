"""
Integration API Tests for AnalytiCore
Tests Google Sheets status, MySQL connection, PostgreSQL connection APIs

Features tested:
- Google Sheets Status API (/api/integrations/google-sheets/status)
- MySQL Connection Test API (/api/integrations/mysql/test)
- PostgreSQL Connection Test API (/api/integrations/postgresql/test)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


@pytest.fixture
def auth_token():
    """Get authentication token via login"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture
def authenticated_headers(auth_token):
    """Headers with auth token"""
    return {
        "Authorization": f"Token {auth_token}",
        "Content-Type": "application/json"
    }


class TestGoogleSheetsStatus:
    """Google Sheets Status API tests"""

    def test_status_requires_authentication(self):
        """Should return 401 without auth token"""
        response = requests.get(f"{BASE_URL}/api/integrations/google-sheets/status")
        assert response.status_code == 401
        print("PASS: Google Sheets status requires authentication (401)")

    def test_status_returns_configured_false_when_no_credentials(self, authenticated_headers):
        """Should return configured:false when no Google credentials set"""
        response = requests.get(
            f"{BASE_URL}/api/integrations/google-sheets/status",
            headers=authenticated_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert 'connected' in data
        assert 'configured' in data
        assert 'message' in data
        
        # Since GOOGLE_SHEETS_CLIENT_ID is not set, should return configured: false
        assert data['configured'] == False
        assert data['connected'] == False
        assert 'not configured' in data['message'].lower()
        print(f"PASS: Google Sheets status returns configured=false, message='{data['message']}'")


class TestMySQLConnection:
    """MySQL Connection Test API tests"""

    def test_mysql_requires_authentication(self):
        """Should return 401 without auth token"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/mysql/test",
            json={
                "host": "localhost",
                "port": "3306",
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass"
            }
        )
        assert response.status_code == 401
        print("PASS: MySQL test requires authentication (401)")

    def test_mysql_connection_with_invalid_host(self, authenticated_headers):
        """Should return failure for invalid connection params"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/mysql/test",
            headers=authenticated_headers,
            json={
                "host": "invalid-host-12345.local",
                "port": "3306",
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass"
            }
        )
        # Should return 400 with connection failure
        assert response.status_code == 400
        data = response.json()
        
        # Verify response structure
        assert 'success' in data
        assert 'message' in data
        assert data['success'] == False
        assert 'failed' in data['message'].lower() or 'connection' in data['message'].lower()
        print(f"PASS: MySQL returns proper error for invalid host: {data['message'][:100]}")

    def test_mysql_connection_accepts_all_params(self, authenticated_headers):
        """Should accept host, port, database, user, password params"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/mysql/test",
            headers=authenticated_headers,
            json={
                "host": "localhost",
                "port": "3306",
                "database": "mydb",
                "user": "root",
                "password": "pass123"
            }
        )
        # Will fail to connect but should process all params (400)
        assert response.status_code == 400
        data = response.json()
        assert 'success' in data
        assert 'message' in data
        print(f"PASS: MySQL API accepts all connection params, returns: {data['success']}")


class TestPostgreSQLConnection:
    """PostgreSQL Connection Test API tests"""

    def test_postgresql_requires_authentication(self):
        """Should return 401 without auth token"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/postgresql/test",
            json={
                "host": "localhost",
                "port": "5432",
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass"
            }
        )
        assert response.status_code == 401
        print("PASS: PostgreSQL test requires authentication (401)")

    def test_postgresql_connection_with_invalid_host(self, authenticated_headers):
        """Should return failure for invalid connection params"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/postgresql/test",
            headers=authenticated_headers,
            json={
                "host": "invalid-host-12345.local",
                "port": "5432",
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass"
            }
        )
        # Should return 400 with connection failure
        assert response.status_code == 400
        data = response.json()
        
        # Verify response structure
        assert 'success' in data
        assert 'message' in data
        assert data['success'] == False
        assert 'failed' in data['message'].lower() or 'connection' in data['message'].lower() or 'could not translate' in data['message'].lower()
        print(f"PASS: PostgreSQL returns proper error for invalid host: {data['message'][:100]}")

    def test_postgresql_connection_accepts_all_params(self, authenticated_headers):
        """Should accept host, port, database, user, password params"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/postgresql/test",
            headers=authenticated_headers,
            json={
                "host": "localhost",
                "port": "5432",
                "database": "mydb",
                "user": "postgres",
                "password": "pass123"
            }
        )
        # Will fail to connect but should process all params (400)
        assert response.status_code == 400
        data = response.json()
        assert 'success' in data
        assert 'message' in data
        print(f"PASS: PostgreSQL API accepts all connection params, returns: {data['success']}")


class TestGoogleSheetsAuth:
    """Google Sheets Auth URL API tests"""

    def test_auth_url_returns_error_when_not_configured(self, authenticated_headers):
        """Should return error when Google credentials not configured"""
        response = requests.get(
            f"{BASE_URL}/api/integrations/google-sheets/auth",
            headers=authenticated_headers
        )
        # Should return 400 when credentials not configured
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
        assert 'not configured' in data['error'].lower() or 'client_id' in data['error'].lower()
        print(f"PASS: Google Sheets auth returns proper error: {data['error'][:100]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
