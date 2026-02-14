#!/usr/bin/env python3
"""
DataPulse Backend API Testing Suite with MongoDB Direct User Creation
Tests all API endpoints including authenticated ones by creating a verified user directly
"""

import requests
import sys
import json
import io
import os
from datetime import datetime, timezone
from pathlib import Path
import bcrypt
import uuid
import pymongo

class DataPulseAPITesterWithAuth:
    def __init__(self, base_url="https://analyticore-preview.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_user_email = f"verified_test_{datetime.now().strftime('%H%M%S')}@example.com"
        self.test_user_name = "Verified Test User"
        self.test_password = "TestPass123!"
        self.tests_run = 0
        self.tests_passed = 0
        self.project_id = None
        self.user_id = None
        
        # MongoDB connection
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.mongo_client["test_database"]
        
        print(f"🚀 Starting DataPulse API Tests with Direct User Creation")
        print(f"📍 Base URL: {base_url}")
        print(f"👤 Test User: {self.test_user_email}")
        print("=" * 80)

    def create_verified_user_in_db(self):
        """Create a verified user directly in MongoDB to bypass email verification"""
        try:
            # Generate user data
            self.user_id = f"user_{uuid.uuid4().hex[:12]}"
            hashed_password = bcrypt.hashpw(self.test_password.encode('utf-8'), bcrypt.gensalt())
            
            user_doc = {
                "user_id": self.user_id,
                "email": self.test_user_email,
                "name": self.test_user_name,
                "password_hash": hashed_password.decode('utf-8'),
                "is_verified": True,  # Skip email verification
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Insert user into database
            result = self.db.users.insert_one(user_doc)
            print(f"✅ Created verified user directly in MongoDB: {self.user_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to create user in MongoDB: {str(e)}")
            return False

    def cleanup_test_user(self):
        """Remove test user from database"""
        try:
            if self.user_id:
                self.db.users.delete_one({"user_id": self.user_id})
                self.db.projects.delete_many({"user_id": self.user_id})
                print(f"🧹 Cleaned up test user: {self.user_id}")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {str(e)}")

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test with detailed logging"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        print(f"   Method: {method} | Endpoint: {endpoint}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=data)
            elif method == 'POST':
                if files:
                    response = self.session.post(url, data=data, files=files)
                else:
                    response = self.session.post(url, json=data)
            elif method == 'PUT':
                response = self.session.put(url, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"   ✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) <= 100:
                        print(f"   📄 Response: {response_data}")
                    elif isinstance(response_data, list) and len(response_data) <= 2:
                        print(f"   📄 Response: {len(response_data)} items")
                    else:
                        print(f"   📄 Response: Large data received")
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

    def test_user_login(self):
        """Test user login with the verified user"""
        success, response = self.run_test(
            "User Login (Verified User)",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.test_user_email,
                "password": self.test_password
            }
        )
        if success and 'user' in response:
            print(f"   👤 Logged in as: {response['user']['name']}")
        return success

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_create_project(self):
        """Test creating a new project"""
        success, response = self.run_test(
            "Create Project",
            "POST",
            "projects",
            200,
            data={
                "name": f"Test Project {datetime.now().strftime('%H:%M:%S')}",
                "source_type": "file_upload"
            }
        )
        if success and 'project_id' in response:
            self.project_id = response['project_id']
            print(f"   📁 Created project: {self.project_id}")
        return success

    def test_get_projects(self):
        """Test getting user projects"""
        success, response = self.run_test(
            "Get Projects",
            "GET",
            "projects",
            200
        )
        if success and isinstance(response, list):
            print(f"   📊 Found {len(response)} projects")
        return success

    def test_file_upload(self):
        """Test file upload with sample CSV data"""
        if not self.project_id:
            print(f"\n⚠️  Skipping file upload test - no project created")
            return False

        # Create sample CSV data
        csv_content = """name,age,city,salary
John Doe,25,New York,50000
Jane Smith,30,Los Angeles,60000
Bob Johnson,35,Chicago,55000
Alice Brown,28,Houston,52000
Charlie Wilson,32,Phoenix,58000"""

        success, response = self.run_test(
            "File Upload",
            "POST",
            f"projects/{self.project_id}/upload",
            200,
            files={'file': ('test_data.csv', csv_content, 'text/csv')}
        )
        
        if success and 'statistics' in response:
            stats = response['statistics']
            print(f"   📊 Data stats: {stats['total_rows']} rows, {stats['total_columns']} columns")
        
        return success

    def test_get_project_data(self):
        """Test getting project data preview"""
        if not self.project_id:
            print(f"\n⚠️  Skipping data preview test - no project created")
            return False

        success, response = self.run_test(
            "Get Project Data",
            "GET",
            f"projects/{self.project_id}/data",
            200
        )
        
        if success and 'data' in response:
            print(f"   📄 Data preview: {len(response['data'])} rows loaded")
        
        return success

    def test_ai_analysis(self):
        """Test AI-powered data analysis"""
        if not self.project_id:
            print(f"\n⚠️  Skipping AI analysis test - no project created")
            return False

        print(f"\n🤖 AI Analysis Test (may take 10-15 seconds for GPT-5.2 processing)")
        success, response = self.run_test(
            "AI Data Analysis",
            "POST",
            f"projects/{self.project_id}/analyze",
            200
        )
        
        if success and 'recommendations' in response:
            recs = response['recommendations']
            print(f"   🧠 AI Recommendations: {len(recs)} suggestions received")
            for i, rec in enumerate(recs[:2]):  # Show first 2 recommendations
                print(f"      {i+1}. {rec.get('column', 'N/A')}: {rec.get('recommendation', 'N/A')[:50]}...")
        
        return success

    def test_data_transformation(self):
        """Test applying data transformations"""
        if not self.project_id:
            print(f"\n⚠️  Skipping transformation test - no project created")
            return False

        # Sample transformation rule
        transformation_rules = [
            {
                "column": "salary",
                "action": "fill_missing",
                "parameters": {"strategy": "mean"}
            }
        ]

        success, response = self.run_test(
            "Apply Data Transformations",
            "POST",
            f"projects/{self.project_id}/transform",
            200,
            data=transformation_rules
        )
        
        if success and 'new_shape' in response:
            print(f"   🔄 Transformation result: {response['new_shape']} final shape")
        
        return success

    def test_logout(self):
        """Test user logout"""
        success, response = self.run_test(
            "User Logout",
            "POST",
            "auth/logout",
            200
        )
        return success

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print(f"🔬 COMPREHENSIVE API TESTING STARTED")
        
        # Create verified user in database
        if not self.create_verified_user_in_db():
            print(f"❌ Failed to create verified user. Stopping tests.")
            return 1
        
        try:
            # Authentication Tests
            print(f"\n" + "="*50 + " AUTHENTICATION TESTS " + "="*50)
            auth_tests = [
                ("Login", self.test_user_login),
                ("Get Current User", self.test_get_current_user),
            ]
            
            auth_passed = 0
            for test_name, test_func in auth_tests:
                if test_func():
                    auth_passed += 1
            
            # Project Management Tests
            project_passed = 0
            if auth_passed >= 1:  # At least login works
                print(f"\n" + "="*50 + " PROJECT MANAGEMENT TESTS " + "="*50)
                project_tests = [
                    ("Create Project", self.test_create_project),
                    ("Get Projects", self.test_get_projects),
                    ("File Upload", self.test_file_upload),
                    ("Get Project Data", self.test_get_project_data),
                    ("AI Analysis", self.test_ai_analysis),
                    ("Data Transformation", self.test_data_transformation),
                ]
                
                for test_name, test_func in project_tests:
                    if test_func():
                        project_passed += 1
            else:
                print(f"\n⚠️  Skipping project tests due to authentication failures")
            
            # Cleanup
            print(f"\n" + "="*50 + " CLEANUP " + "="*50)
            self.test_logout()
            
            # Final Results
            print(f"\n" + "="*50 + " FINAL RESULTS " + "="*50)
            success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
            print(f"📊 Tests Passed: {self.tests_passed}/{self.tests_run} ({success_rate:.1f}%)")
            print(f"🔐 Authentication: {auth_passed}/2 tests passed")
            print(f"📁 Project Management: {project_passed}/6 tests passed")
            
            # Determine overall success
            critical_failures = []
            if auth_passed < 1:
                critical_failures.append("Authentication system has issues")
            if project_passed < 4 and auth_passed >= 1:
                critical_failures.append("Project management has issues")
                
            if critical_failures:
                print(f"\n🚨 CRITICAL ISSUES FOUND:")
                for issue in critical_failures:
                    print(f"   • {issue}")
                return 1
            else:
                print(f"\n✅ BACKEND TESTING COMPLETED SUCCESSFULLY")
                return 0
        finally:
            self.cleanup_test_user()

def main():
    """Main test execution"""
    tester = DataPulseAPITesterWithAuth()
    return tester.run_comprehensive_test()

if __name__ == "__main__":
    sys.exit(main())