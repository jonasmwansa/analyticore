#!/usr/bin/env python3
"""
AnalytiCore Django REST Framework Backend API Testing Suite
Tests authentication, projects, AI analysis, transformations, exports, admin dashboard, and data sources
"""

import requests
import sys
import json
import io
import os
from datetime import datetime

class AnalyticoreAPITester:
    def __init__(self, base_url="https://etl-autopilot.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_session = requests.Session()
        self.test_user_email = f"test_user_{datetime.now().strftime('%H%M%S')}@analyticore.com"
        self.test_user_name = "Test User"
        self.test_password = "TestPass123!"
        self.admin_email = "admin@analyticore.com"
        self.admin_password = "admin123"
        self.tests_run = 0
        self.tests_passed = 0
        self.project_id = None
        self.admin_token = None
        print(f"🚀 Starting AnalytiCore API Tests")
        print(f"📍 Base URL: {base_url}")
        print(f"👤 Test User: {self.test_user_email}")
        print(f"👑 Admin User: {self.admin_email}")
        print("=" * 80)

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, session=None):
        """Run a single API test with detailed logging"""
        if session is None:
            session = self.session
            
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        print(f"   Method: {method} | Endpoint: {endpoint}")
        
        try:
            if method == 'GET':
                response = session.get(url, params=data)
            elif method == 'POST':
                if files:
                    response = session.post(url, data=data, files=files)
                else:
                    response = session.post(url, json=data)
            elif method == 'PATCH':
                response = session.patch(url, json=data)
            elif method == 'DELETE':
                response = session.delete(url)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"   ✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 200:
                        print(f"   📄 Response: {response_data}")
                    elif isinstance(response_data, list) and len(response_data) <= 3:
                        print(f"   📄 Response: {len(response_data)} items")
                    else:
                        print(f"   📄 Response: Large data object received")
                except:
                    print(f"   📄 Response: Non-JSON response")
            else:
                print(f"   ❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   🚨 Error: {error_detail}")
                except:
                    print(f"   🚨 Error: {response.text[:200]}...")

            return success, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text

        except requests.exceptions.RequestException as e:
            print(f"   ❌ FAILED - Network Error: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"   ❌ FAILED - Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration with email verification"""
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            201,
            data={
                "email": self.test_user_email,
                "password": self.test_password,
                "name": self.test_user_name
            }
        )
        return success

    def test_admin_login(self):
        """Test admin user login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.admin_email,
                "password": self.admin_password
            },
            session=self.admin_session
        )
        
        if success and 'token' in response:
            self.admin_token = response['token']
            self.admin_session.headers.update({'Authorization': f'Token {self.admin_token}'})
            print(f"   👑 Admin logged in with token")
        return success

    def test_user_login_unverified(self):
        """Test user login without email verification (should fail)"""
        success, response = self.run_test(
            "User Login (Unverified - Expected to Fail)",
            "POST", 
            "auth/login",
            400,  # Expecting failure due to unverified email
            data={
                "email": self.test_user_email,
                "password": self.test_password
            }
        )
        # For this test, success means we got the expected error status
        return success

    def test_google_auth_callback(self):
        """Test Google OAuth callback endpoint"""
        success, response = self.run_test(
            "Google Auth Callback (No Session)",
            "GET",
            "auth/session",
            400,  # Expected to fail without session_id
            data={}
        )
        # This should fail without session_id, which is expected behavior
        return success

    def test_get_current_user(self):
        """Test getting current user info (admin)"""
        success, response = self.run_test(
            "Get Current User (Admin)",
            "GET",
            "auth/me",
            200,
            session=self.admin_session
        )
        if success and 'email' in response:
            print(f"   👤 Current user: {response['email']}")
        return success

    def test_create_project(self):
        """Test creating a new project (as admin)"""
        success, response = self.run_test(
            "Create Project",
            "POST",
            "projects/",
            201,
            data={
                "name": f"Test Project {datetime.now().strftime('%H:%M:%S')}",
                "description": "Test project for API testing",
                "source_type": "file_upload"
            },
            session=self.admin_session
        )
        
        if success:
            # After creation, get the project list to find the created project
            if 'project_id' in response:
                self.project_id = response['project_id']
                print(f"   📁 Created project: {self.project_id}")
            else:
                # If project_id not in response, get it from project list
                projects_success, projects_response = self.run_test(
                    "Get Projects to Find Created Project",
                    "GET",
                    "projects/",
                    200,
                    session=self.admin_session
                )
                if projects_success and 'results' in projects_response and len(projects_response['results']) > 0:
                    # Find the most recent project (first in the list due to ordering)
                    latest_project = projects_response['results'][0]
                    self.project_id = latest_project.get('project_id')
                    print(f"   📁 Found created project ID: {self.project_id}")
                else:
                    print(f"   ⚠️  Could not retrieve project ID from response")
        
        return success

    def test_get_projects(self):
        """Test getting user projects"""
        success, response = self.run_test(
            "Get Projects",
            "GET", 
            "projects/",
            200,
            session=self.admin_session
        )
        if success and isinstance(response, list):
            print(f"   📊 Found {len(response)} projects")
        return success

    def test_file_upload(self):
        """Test file upload with sample CSV data"""
        if not self.project_id:
            print(f"\n⚠️  Skipping file upload test - no project created")
            return False

        # Create sample CSV data with missing values and outliers for AI analysis
        csv_content = """name,age,city,salary,experience
John Doe,25,New York,50000,2
Jane Smith,,Los Angeles,60000,5
Bob Johnson,35,Chicago,55000,8
Alice Brown,28,Houston,,3
Charlie Wilson,32,Phoenix,58000,6
David Miller,29,Boston,52000,4
Eva Garcia,31,,59000,7
Frank Lee,27,Seattle,51000,3
Grace Wang,33,Denver,61000,9
Henry Adams,26,Austin,49000,2
Iris Chen,200,Miami,1000000,15
"""

        success, response = self.run_test(
            "File Upload",
            "POST",
            f"projects/{self.project_id}/upload",
            200,
            files={'file': ('test_data.csv', csv_content, 'text/csv')},
            session=self.admin_session
        )
        
        if success:
            print(f"   📊 File uploaded successfully")
        
        return success

    def test_get_project_data(self):
        """Test getting project data preview"""
        if not self.project_id:
            print(f"\n⚠️  Skipping data preview test - no project created")
            return False

        success, response = self.run_test(
            "Get Project Data Preview",
            "GET",
            f"projects/{self.project_id}/data",
            200,
            session=self.admin_session
        )
        
        if success:
            print(f"   📄 Data preview loaded")
        
        return success

    def test_ai_analysis(self):
        """Test AI-powered data analysis using GPT-5.2"""
        if not self.project_id:
            print(f"\n⚠️  Skipping AI analysis test - no project created")
            return False

        print(f"\n🤖 AI Analysis Test (may take 10-15 seconds for GPT-5.2 processing)")
        success, response = self.run_test(
            "AI Data Analysis",
            "POST",
            f"analysis/{self.project_id}/analyze",
            200,
            session=self.admin_session
        )
        
        if success and 'recommendations' in response:
            recs = response['recommendations']
            print(f"   🧠 AI Recommendations: {len(recs)} suggestions received")
            for i, rec in enumerate(recs[:3]):  # Show first 3 recommendations
                print(f"      {i+1}. {rec.get('column', 'N/A')}: {rec.get('recommendation', 'N/A')[:50]}...")
        
        return success

    def test_data_transformation(self):
        """Test applying data transformations"""
        if not self.project_id:
            print(f"\n⚠️  Skipping transformation test - no project created")
            return False

        # Sample transformation rules
        transformation_rules = [
            {
                "column": "age",
                "action": "fill_missing", 
                "parameters": {"strategy": "mean"}
            },
            {
                "column": "salary",
                "action": "remove_outliers",
                "parameters": {}
            }
        ]

        success, response = self.run_test(
            "Apply Data Transformations",
            "POST",
            f"analysis/{self.project_id}/transform",
            200,
            data={"rules": transformation_rules},
            session=self.admin_session
        )
        
        if success and 'new_shape' in response:
            print(f"   🔄 Transformation result: {response['new_shape']} final shape")
        
        return success

    def test_export_data(self):
        """Test data export functionality"""
        if not self.project_id:
            print(f"\n⚠️  Skipping export test - no project created")
            return False

        success, response = self.run_test(
            "Export Data (CSV)",
            "GET",
            f"exports/{self.project_id}/export?format=csv",
            200,
            session=self.admin_session
        )
        
        return success

    def test_generate_charts(self):
        """Test chart generation with Plotly"""
        if not self.project_id:
            print(f"\n⚠️  Skipping charts test - no project created")
            return False

        success, response = self.run_test(
            "Generate Charts",
            "GET", 
            f"exports/{self.project_id}/charts?type=summary",
            200,
            session=self.admin_session
        )
        
        if success and 'charts' in response:
            charts = response['charts']
            print(f"   📊 Generated {len(charts)} charts")
        
        return success

    def test_mysql_connection(self):
        """Test MySQL connection endpoint"""
        success, response = self.run_test(
            "MySQL Connection Test (Invalid Credentials)",
            "POST",
            "integrations/mysql/test",
            400,  # Expected to fail with invalid credentials
            data={
                "host": "localhost",
                "port": 3306,
                "user": "test",
                "password": "test",
                "database": "test"
            },
            session=self.admin_session
        )
        
        return success

    def test_list_data_sources(self):
        """Test listing data sources"""
        success, response = self.run_test(
            "List Data Sources",
            "GET",
            "integrations/sources",
            200,
            session=self.admin_session
        )
        
        if success and 'data_sources' in response:
            sources = response['data_sources']
            print(f"   🔗 Found {len(sources)} data sources")
        
        return success

    def test_admin_dashboard_stats(self):
        """Test admin dashboard statistics"""
        success, response = self.run_test(
            "Admin Dashboard Stats",
            "GET",
            "saas-admin/dashboard",
            200,
            session=self.admin_session
        )
        
        if success and 'overview' in response:
            overview = response['overview']
            print(f"   📈 Admin Stats: {overview.get('total_users', 0)} users, {overview.get('total_projects', 0)} projects")
        
        return success

    def test_admin_users_list(self):
        """Test admin users list"""
        success, response = self.run_test(
            "Admin Users List", 
            "GET",
            "saas-admin/users",
            200,
            session=self.admin_session
        )
        
        if success and 'users' in response:
            users = response['users']
            print(f"   👥 Admin found {len(users)} users")
        
        return success

    def test_admin_projects_list(self):
        """Test admin projects list"""
        success, response = self.run_test(
            "Admin Projects List",
            "GET", 
            "saas-admin/projects",
            200,
            session=self.admin_session
        )
        
        if success and 'projects' in response:
            projects = response['projects']
            print(f"   📁 Admin found {len(projects)} projects")
        
        return success

    def test_protected_route_without_auth(self):
        """Test accessing protected route without authentication"""
        # Create a new session without auth
        unauth_session = requests.Session()
        
        success, response = self.run_test(
            "Protected Route Without Auth",
            "GET",
            "projects/",
            401,  # Expected unauthorized
            session=unauth_session
        )
        
        return success

    def test_logout(self):
        """Test user logout"""
        success, response = self.run_test(
            "User Logout",
            "POST",
            "auth/logout",
            200,
            session=self.admin_session
        )
        return success

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print(f"🔬 COMPREHENSIVE ANALYTICORE API TESTING STARTED")
        
        # Authentication Tests
        print(f"\n" + "="*60 + " AUTHENTICATION TESTS " + "="*60)
        auth_tests = [
            ("User Registration", self.test_user_registration),
            ("Admin Login", self.test_admin_login),  
            ("User Login (Unverified)", self.test_user_login_unverified),
            ("Google Auth Callback", self.test_google_auth_callback),
            ("Get Current User", self.test_get_current_user),
            ("Protected Route (No Auth)", self.test_protected_route_without_auth),
        ]
        
        auth_passed = 0
        for test_name, test_func in auth_tests:
            if test_func():
                auth_passed += 1

        # Project Management Tests (requires admin login)
        project_passed = 0
        if self.admin_token:
            print(f"\n" + "="*60 + " PROJECT MANAGEMENT TESTS " + "="*60)
            project_tests = [
                ("Create Project", self.test_create_project),
                ("Get Projects", self.test_get_projects), 
                ("File Upload", self.test_file_upload),
                ("Get Project Data", self.test_get_project_data),
            ]
            
            for test_name, test_func in project_tests:
                if test_func():
                    project_passed += 1

            # AI & Data Processing Tests
            print(f"\n" + "="*60 + " AI & DATA PROCESSING TESTS " + "="*60)
            ai_tests = [
                ("AI Analysis", self.test_ai_analysis),
                ("Data Transformation", self.test_data_transformation),
                ("Export Data", self.test_export_data), 
                ("Generate Charts", self.test_generate_charts),
            ]
            
            ai_passed = 0
            for test_name, test_func in ai_tests:
                if test_func():
                    ai_passed += 1

            # Admin Dashboard Tests
            print(f"\n" + "="*60 + " ADMIN DASHBOARD TESTS " + "="*60)
            admin_tests = [
                ("Admin Dashboard Stats", self.test_admin_dashboard_stats),
                ("Admin Users List", self.test_admin_users_list),
                ("Admin Projects List", self.test_admin_projects_list),
            ]
            
            admin_passed = 0
            for test_name, test_func in admin_tests:
                if test_func():
                    admin_passed += 1

            # Data Integration Tests
            print(f"\n" + "="*60 + " DATA INTEGRATION TESTS " + "="*60)
            integration_tests = [
                ("MySQL Connection Test", self.test_mysql_connection),
                ("List Data Sources", self.test_list_data_sources),
            ]
            
            integration_passed = 0
            for test_name, test_func in integration_tests:
                if test_func():
                    integration_passed += 1

        else:
            print(f"\n⚠️  Skipping project tests - admin login failed")
            ai_passed = admin_passed = integration_passed = 0

        # Cleanup
        print(f"\n" + "="*60 + " CLEANUP " + "="*60)
        self.test_logout()

        # Final Results
        print(f"\n" + "="*60 + " FINAL RESULTS " + "="*60)
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📊 Tests Passed: {self.tests_passed}/{self.tests_run} ({success_rate:.1f}%)")
        print(f"🔐 Authentication: {auth_passed}/6 tests passed")
        
        if self.admin_token:
            print(f"📁 Project Management: {project_passed}/4 tests passed")
            print(f"🤖 AI & Data Processing: {ai_passed}/4 tests passed")
            print(f"👑 Admin Dashboard: {admin_passed}/3 tests passed")
            print(f"🔗 Data Integration: {integration_passed}/2 tests passed")
        
        # Determine overall success
        critical_failures = []
        if auth_passed < 4:
            critical_failures.append(f"Authentication system issues ({auth_passed}/6 passed)")
        if self.admin_token and project_passed < 3:
            critical_failures.append(f"Project management issues ({project_passed}/4 passed)")
        if self.admin_token and ai_passed < 2:
            critical_failures.append(f"AI processing issues ({ai_passed}/4 passed)")
            
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in critical_failures:
                print(f"   • {issue}")
            return 1
        else:
            print(f"\n✅ ANALYTICORE BACKEND TESTING COMPLETED SUCCESSFULLY")
            return 0

def main():
    """Main test execution"""
    tester = AnalyticoreAPITester()
    return tester.run_comprehensive_test()

if __name__ == "__main__":
    sys.exit(main())