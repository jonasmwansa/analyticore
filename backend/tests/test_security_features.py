"""
Security Features API Tests
Tests for: Password Reset, Password Validation, 2FA, Admin Alert Settings
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@analyticore.com"
ADMIN_PASSWORD = "adminpassword"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass123"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Admin authentication failed - skipping admin tests")


@pytest.fixture(scope="module")
def user_token(api_client):
    """Get regular user authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("User authentication failed - skipping user tests")


class TestPasswordValidation:
    """Password validation endpoint tests"""
    
    def test_validate_weak_password_short(self, api_client):
        """Test that short passwords fail validation"""
        response = api_client.post(f"{BASE_URL}/api/auth/password/validate", json={
            "password": "Short1!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] == False
        assert 'requirements' in data
        assert data['requirements']['length']['met'] == False
    
    def test_validate_password_no_uppercase(self, api_client):
        """Test that passwords without uppercase fail"""
        response = api_client.post(f"{BASE_URL}/api/auth/password/validate", json={
            "password": "alllowercase123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] == False
        assert data['requirements']['uppercase']['met'] == False
    
    def test_validate_password_no_lowercase(self, api_client):
        """Test that passwords without lowercase fail"""
        response = api_client.post(f"{BASE_URL}/api/auth/password/validate", json={
            "password": "ALLUPPERCASE123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] == False
        assert data['requirements']['lowercase']['met'] == False
    
    def test_validate_password_no_digit(self, api_client):
        """Test that passwords without digits fail"""
        response = api_client.post(f"{BASE_URL}/api/auth/password/validate", json={
            "password": "NoDigitsHere!@#"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] == False
        assert data['requirements']['digit']['met'] == False
    
    def test_validate_password_no_special(self, api_client):
        """Test that passwords without special characters fail"""
        response = api_client.post(f"{BASE_URL}/api/auth/password/validate", json={
            "password": "NoSpecialChar123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] == False
        assert data['requirements']['special']['met'] == False
    
    def test_validate_strong_password(self, api_client):
        """Test that strong password passes all requirements"""
        response = api_client.post(f"{BASE_URL}/api/auth/password/validate", json={
            "password": "StrongPass123!@#"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] == True
        assert data['strength'] == 100
        assert all(req['met'] for req in data['requirements'].values())


class TestPasswordResetRequest:
    """Password reset request endpoint tests"""
    
    def test_reset_request_with_valid_email(self, api_client):
        """Test password reset request with valid email"""
        response = api_client.post(f"{BASE_URL}/api/auth/password/reset-request", json={
            "email": ADMIN_EMAIL
        })
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
    
    def test_reset_request_with_invalid_email(self, api_client):
        """Test password reset request with non-existent email (should still return success for security)"""
        response = api_client.post(f"{BASE_URL}/api/auth/password/reset-request", json={
            "email": "nonexistent@example.com"
        })
        # Should return 200 to prevent email enumeration
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
    
    def test_reset_request_without_email(self, api_client):
        """Test password reset request without email"""
        response = api_client.post(f"{BASE_URL}/api/auth/password/reset-request", json={})
        assert response.status_code == 400
        data = response.json()
        assert 'detail' in data


class TestSecuritySettings:
    """Security settings endpoint tests"""
    
    def test_get_security_settings_authenticated(self, api_client, user_token):
        """Test getting security settings for authenticated user"""
        response = api_client.get(
            f"{BASE_URL}/api/auth/security/settings",
            headers={"Authorization": f"Token {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert 'two_factor_enabled' in data
        assert 'two_factor_method' in data
        assert isinstance(data['two_factor_enabled'], bool)
    
    def test_get_security_settings_unauthenticated(self, api_client):
        """Test that security settings require authentication"""
        response = api_client.get(f"{BASE_URL}/api/auth/security/settings")
        assert response.status_code == 401


class Test2FA:
    """Two-factor authentication tests"""
    
    def test_enable_2fa_unauthenticated(self, api_client):
        """Test that enabling 2FA requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/auth/2fa/enable", json={
            "method": "email"
        })
        assert response.status_code == 401
    
    def test_disable_2fa_unauthenticated(self, api_client):
        """Test that disabling 2FA requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/auth/2fa/disable", json={
            "password": "somepassword"
        })
        assert response.status_code == 401
    
    def test_invalid_2fa_method(self, api_client, user_token):
        """Test enabling 2FA with invalid method"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/2fa/enable",
            headers={"Authorization": f"Token {user_token}"},
            json={"method": "sms"}  # SMS not supported, only email
        )
        assert response.status_code == 400
        data = response.json()
        assert 'detail' in data


class TestAdminAlertSettings:
    """Admin alert settings tests"""
    
    def test_get_alert_settings_admin(self, api_client, admin_token):
        """Test getting alert settings as admin"""
        response = api_client.get(
            f"{BASE_URL}/api/saas-admin/settings/alerts",
            headers={"Authorization": f"Token {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert 'error_rate_threshold' in data
        assert 'db_response_threshold_ms' in data
        assert 'max_errors_24h' in data
        assert 'alert_emails_enabled' in data
        assert 'daily_summary_enabled' in data
        assert 'health_check_interval_minutes' in data
    
    def test_get_alert_settings_non_admin(self, api_client, user_token):
        """Test that non-admin cannot access alert settings"""
        response = api_client.get(
            f"{BASE_URL}/api/saas-admin/settings/alerts",
            headers={"Authorization": f"Token {user_token}"}
        )
        assert response.status_code == 403
    
    def test_get_alert_settings_unauthenticated(self, api_client):
        """Test that alert settings require authentication"""
        response = api_client.get(f"{BASE_URL}/api/saas-admin/settings/alerts")
        assert response.status_code == 401
    
    def test_update_alert_settings_admin(self, api_client, admin_token):
        """Test updating alert settings as admin"""
        # First get current settings
        get_response = api_client.get(
            f"{BASE_URL}/api/saas-admin/settings/alerts",
            headers={"Authorization": f"Token {admin_token}"}
        )
        original = get_response.json()
        
        # Update settings
        new_threshold = 7.5 if original.get('error_rate_threshold', 5) != 7.5 else 5.0
        response = api_client.put(
            f"{BASE_URL}/api/saas-admin/settings/alerts/update",
            headers={"Authorization": f"Token {admin_token}"},
            json={"error_rate_threshold": new_threshold}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['error_rate_threshold'] == new_threshold
        
        # Verify it persisted
        verify_response = api_client.get(
            f"{BASE_URL}/api/saas-admin/settings/alerts",
            headers={"Authorization": f"Token {admin_token}"}
        )
        assert verify_response.json()['error_rate_threshold'] == new_threshold
        
        # Restore original
        api_client.put(
            f"{BASE_URL}/api/saas-admin/settings/alerts/update",
            headers={"Authorization": f"Token {admin_token}"},
            json={"error_rate_threshold": original.get('error_rate_threshold', 5)}
        )
    
    def test_update_alert_settings_invalid_threshold(self, api_client, admin_token):
        """Test updating alert settings with invalid threshold"""
        response = api_client.put(
            f"{BASE_URL}/api/saas-admin/settings/alerts/update",
            headers={"Authorization": f"Token {admin_token}"},
            json={"error_rate_threshold": 150}  # Over 100%
        )
        assert response.status_code == 400
    
    def test_update_alert_settings_non_admin(self, api_client, user_token):
        """Test that non-admin cannot update alert settings"""
        response = api_client.put(
            f"{BASE_URL}/api/saas-admin/settings/alerts/update",
            headers={"Authorization": f"Token {user_token}"},
            json={"error_rate_threshold": 5}
        )
        assert response.status_code == 403


class TestPasswordUpdate:
    """Password update endpoint tests (for authenticated users)"""
    
    def test_update_password_unauthenticated(self, api_client):
        """Test that password update requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/auth/password/update", json={
            "current_password": "oldpass",
            "new_password": "NewPass123!@#"
        })
        assert response.status_code == 401
    
    def test_update_password_missing_fields(self, api_client, user_token):
        """Test password update with missing fields"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/password/update",
            headers={"Authorization": f"Token {user_token}"},
            json={"new_password": "NewPass123!@#"}  # Missing current_password
        )
        assert response.status_code == 400


class TestSecurityAuditLog:
    """Security audit log tests"""
    
    def test_get_audit_log_authenticated(self, api_client, user_token):
        """Test getting security audit log for authenticated user"""
        response = api_client.get(
            f"{BASE_URL}/api/auth/security/audit-log",
            headers={"Authorization": f"Token {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert 'logs' in data
        assert isinstance(data['logs'], list)
    
    def test_get_audit_log_unauthenticated(self, api_client):
        """Test that audit log requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/auth/security/audit-log")
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
