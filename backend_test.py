#!/usr/bin/env python3
"""
Comprehensive Backend Test for Enhanced Visualization and Export Features
Tests smart chart recommendations, LLM chart insights, and all export endpoints.
"""
import requests
import json
import base64
import csv
import io
import time
import os
import sys
import tempfile
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://private-analyst.preview.emergentagent.com/api"
TEST_EMAIL = "verified_test@example.com"  
TEST_PASSWORD = "TestPassword123!"
PROJECT_NAME = "Chart Intelligence Test"

# Test CSV data with mixed data types for comprehensive testing
TEST_CSV_DATA = """name,age,salary,department,performance_score,years_experience,city,satisfaction_rating
Alice Johnson,28,65000,Engineering,8.5,3.2,San Francisco,4.2
Bob Smith,34,75000,Marketing,7.8,5.1,New York,3.8
Carol Davis,29,58000,Engineering,9.1,2.8,Seattle,4.5
David Wilson,41,92000,Sales,6.9,8.5,Chicago,3.2
Emma Brown,26,52000,Marketing,8.7,1.9,Austin,4.1
Frank Miller,38,88000,Engineering,7.4,6.3,San Francisco,3.9
Grace Lee,31,67000,Sales,8.9,4.7,New York,4.3
Henry Taylor,45,105000,Management,7.2,12.1,Seattle,3.6
Ivy Chen,27,61000,Engineering,9.3,2.1,San Francisco,4.7
Jack Anderson,33,79000,Marketing,7.6,5.8,Chicago,3.5
Karen White,30,73000,Sales,8.1,4.2,Austin,4.0
Liam Garcia,37,85000,Management,7.9,7.4,New York,3.8
Maria Rodriguez,25,49000,Marketing,8.4,1.5,Seattle,4.2
Noah Kim,42,98000,Engineering,7.1,9.2,San Francisco,3.4
Olivia Jones,29,64000,Sales,8.8,3.6,Chicago,4.4
Paul Thompson,36,81000,Management,7.7,6.9,Austin,3.7
Quinn Roberts,32,76000,Engineering,8.3,4.8,New York,4.1
Rachel Martinez,28,59000,Marketing,8.6,2.4,Seattle,4.3
Sam Wilson,39,89000,Sales,7.3,7.1,San Francisco,3.3
Tina Clark,35,82000,Management,8.0,6.2,Chicago,3.9
"""

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.project_id = None
        self.pipeline_id = None
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = "", details: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   → {message}")
        if not success and details:
            print(f"   → Details: {details}")
    
    def test_authentication(self) -> bool:
        """Test user registration and login with email verification"""
        try:
            # Register test user
            register_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": "Chart Test"
            }
            
            register_response = self.session.post(
                f"{BASE_URL}/auth/register",
                json=register_data
            )
            
            if register_response.status_code == 400:
                # User already exists, try to login
                self.log_test("User Registration", True, "User already exists, attempting login")
            elif register_response.status_code != 201:
                self.log_test("User Registration", False, 
                            f"Registration failed with status {register_response.status_code}", 
                            register_response.text[:200])
                return False
            else:
                self.log_test("User Registration", True, "New user registered successfully")
                
                # For a new user, we need to verify the email
                # Since we can't access email in tests, we'll try to use an existing verified user
                
            # Try login first to see if user is already verified
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            login_response = self.session.post(
                f"{BASE_URL}/auth/login",
                json=login_data
            )
            
            if login_response.status_code == 200:
                # Login successful
                login_result = login_response.json()
                self.auth_token = login_result.get('token')
                
                if self.auth_token:
                    # Set auth header for all future requests
                    self.session.headers.update({
                        'Authorization': f'Token {self.auth_token}'
                    })
                    self.log_test("Authentication", True, f"User authenticated: {TEST_EMAIL}")
                    return True
                else:
                    self.log_test("Get Auth Token", False, "No token in login response", login_result)
                    return False
            
            # If login failed, check if it's due to email verification
            elif login_response.status_code == 400:
                error_response = login_response.json()
                if "verify your email" in str(error_response).lower():
                    # Try with a different test user that might be verified
                    test_emails = [
                        "testuser@example.com",
                        "admin@example.com",
                        "test@analyticore.com"
                    ]
                    
                    for test_email in test_emails:
                        login_test_data = {
                            "email": test_email,
                            "password": "password123"
                        }
                        
                        test_login_response = self.session.post(
                            f"{BASE_URL}/auth/login",
                            json=login_test_data
                        )
                        
                        if test_login_response.status_code == 200:
                            login_result = test_login_response.json()
                            self.auth_token = login_result.get('token')
                            
                            if self.auth_token:
                                self.session.headers.update({
                                    'Authorization': f'Token {self.auth_token}'
                                })
                                self.log_test("Authentication", True, f"Using existing verified user: {test_email}")
                                return True
                    
                    self.log_test("User Login", False, 
                                "Email verification required and no verified test users available", 
                                error_response)
                    return False
                else:
                    self.log_test("User Login", False, 
                                f"Login failed with status {login_response.status_code}", 
                                error_response)
                    return False
            else:
                self.log_test("User Login", False, 
                            f"Login failed with unexpected status {login_response.status_code}", 
                            login_response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_create_project_and_upload_data(self) -> bool:
        """Test project creation and CSV data upload"""
        try:
            # Create project
            project_data = {
                "name": PROJECT_NAME,
                "description": "Testing enhanced visualization and export features",
                "source_type": "file_upload"
            }
            
            project_response = self.session.post(
                f"{BASE_URL}/projects/",
                json=project_data
            )
            
            if project_response.status_code != 201:
                self.log_test("Project Creation", False,
                            f"Project creation failed with status {project_response.status_code}",
                            project_response.text[:200])
                return False
            
            project_info = project_response.json()
            self.project_id = project_info.get('project_id')
            
            if not self.project_id:
                self.log_test("Project Creation", False, "No project_id in response", project_info)
                return False
            
            self.log_test("Project Creation", True, f"Project created: {self.project_id}")
            
            # Upload CSV data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write(TEST_CSV_DATA)
                csv_file_path = f.name
            
            try:
                with open(csv_file_path, 'rb') as f:
                    files = {
                        'file': ('test_data.csv', f, 'text/csv')
                    }
                    
                    upload_response = self.session.post(
                        f"{BASE_URL}/projects/{self.project_id}/upload",
                        files=files
                    )
                    
                    if upload_response.status_code != 200:
                        self.log_test("CSV Upload", False,
                                    f"Upload failed with status {upload_response.status_code}",
                                    upload_response.text[:200])
                        return False
                    
                    upload_info = upload_response.json()
                    actual_rows = upload_info.get('statistics', {}).get('total_rows', 0)
                    self.log_test("CSV Upload", True, 
                                f"CSV uploaded with {actual_rows} rows and automated analysis completed")
                    return True
                    
            finally:
                os.unlink(csv_file_path)
                
        except Exception as e:
            self.log_test("Project & Upload", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_execution(self) -> bool:
        """Test pipeline execution with smart recommendations"""
        try:
            # Wait a bit to ensure upload process is complete
            time.sleep(2)
            
            # Start pipeline
            start_response = self.session.post(
                f"{BASE_URL}/analysis/pipeline/start/{self.project_id}",
                json={"llm_enabled": True}
            )
            
            if start_response.status_code == 502:
                # Retry once after waiting
                time.sleep(3)
                start_response = self.session.post(
                    f"{BASE_URL}/analysis/pipeline/start/{self.project_id}",
                    json={"llm_enabled": True}
                )
            
            if start_response.status_code == 409:
                # Pipeline already running - get the existing pipeline ID
                error_data = start_response.json()
                self.pipeline_id = error_data.get('pipeline_id')
                if self.pipeline_id:
                    self.log_test("Pipeline Start", True, 
                                f"Using existing pipeline: {self.pipeline_id}")
                else:
                    self.log_test("Pipeline Start", False, 
                                "Pipeline conflict but no ID provided", error_data)
                    return False
            elif start_response.status_code != 200:
                self.log_test("Pipeline Start", False,
                            f"Pipeline start failed with status {start_response.status_code}",
                            start_response.text[:200])
                return False
            else:
                pipeline_info = start_response.json()
                self.pipeline_id = pipeline_info.get('pipeline_id')
                
                if not self.pipeline_id:
                    self.log_test("Pipeline Start", False, "No pipeline_id in response", pipeline_info)
                    return False
                
                self.log_test("Pipeline Start", True, f"New pipeline started: {self.pipeline_id}")
            
            # Monitor pipeline progress
            max_retries = 60  # 60 seconds max
            retry_count = 0
            
            while retry_count < max_retries:
                time.sleep(1)
                status_response = self.session.get(
                    f"{BASE_URL}/analysis/pipeline/{self.pipeline_id}/status"
                )
                
                if status_response.status_code != 200:
                    self.log_test("Pipeline Status Check", False,
                                f"Status check failed with status {status_response.status_code}")
                    return False
                
                status_data = status_response.json()
                pipeline_status = status_data.get('status')
                progress = status_data.get('progress_percent', 0)
                current_stage = status_data.get('current_stage')
                
                if pipeline_status == 'completed':
                    self.log_test("Pipeline Execution", True, 
                                f"Pipeline completed in {retry_count}s, Progress: {progress}%")
                    return True
                elif pipeline_status in ['failed', 'cancelled']:
                    error_msg = status_data.get('error_message', 'Unknown error')
                    self.log_test("Pipeline Execution", False,
                                f"Pipeline {pipeline_status}: {error_msg}")
                    return False
                
                retry_count += 1
            
            self.log_test("Pipeline Execution", False, 
                        f"Pipeline timed out after {max_retries}s")
            return False
            
        except Exception as e:
            self.log_test("Pipeline Execution", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_results_verification(self) -> bool:
        """Verify pipeline results include smart recommendations and LLM insights"""
        try:
            results_response = self.session.get(
                f"{BASE_URL}/analysis/pipeline/{self.pipeline_id}/results"
            )
            
            if results_response.status_code != 200:
                self.log_test("Pipeline Results", False,
                            f"Results fetch failed with status {results_response.status_code}")
                return False
            
            results = results_response.json()
            
            # Check visualization section
            visualization = results.get('visualization', {})
            
            if not visualization:
                self.log_test("Pipeline Results - Visualization", False,
                            "No visualization section in results")
                return False
            
            # Check smart recommendations
            smart_recs = visualization.get('smart_recommendations', {})
            recommendations = smart_recs.get('recommendations', [])
            
            if not recommendations:
                self.log_test("Smart Recommendations", False,
                            "No smart recommendations found")
                return False
            
            # Verify recommendation structure
            first_rec = recommendations[0]
            required_fields = ['chart_type', 'title', 'description', 'columns', 'priority', 'reasoning']
            missing_fields = [field for field in required_fields if field not in first_rec]
            
            if missing_fields:
                self.log_test("Smart Recommendations Structure", False,
                            f"Missing fields: {missing_fields}")
                return False
            
            self.log_test("Smart Recommendations", True,
                        f"Found {len(recommendations)} recommendations with proper structure")
            
            # Check column profiles
            column_profiles = visualization.get('column_profiles', {}) or smart_recs.get('column_profiles', {})
            
            if not column_profiles:
                self.log_test("Column Profiles", False, "No column profiles found")
                return False
            
            self.log_test("Column Profiles", True,
                        f"Found profiles for {len(column_profiles)} columns")
            
            # Check LLM chart insights
            llm_chart_insights = visualization.get('llm_chart_insights', {})
            
            if not llm_chart_insights:
                self.log_test("LLM Chart Insights", False, "No LLM chart insights found")
                return False
            
            # Verify insights structure
            first_insight_key = next(iter(llm_chart_insights))
            first_insight = llm_chart_insights[first_insight_key]
            
            insight_fields = ['title', 'narrative', 'reasoning']
            missing_insight_fields = [field for field in insight_fields if field not in first_insight]
            
            if missing_insight_fields:
                self.log_test("LLM Chart Insights Structure", False,
                            f"Missing insight fields: {missing_insight_fields}")
                return False
            
            self.log_test("LLM Chart Insights", True,
                        f"Found LLM insights for {len(llm_chart_insights)} chart types")
            
            return True
            
        except Exception as e:
            self.log_test("Pipeline Results Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_export_endpoints(self) -> bool:
        """Test all export endpoints with various sections and chart types"""
        all_tests_passed = True
        
        # Test CSV exports
        csv_sections = ['statistics', 'visualizations', 'correlation', 'cleaning', 'insights', 'summary']
        
        for section in csv_sections:
            try:
                csv_response = self.session.get(
                    f"{BASE_URL}/exports/pipeline/{self.pipeline_id}/export-csv",
                    params={'section': section}
                )
                
                if csv_response.status_code != 200:
                    self.log_test(f"CSV Export - {section}", False,
                                f"Failed with status {csv_response.status_code}")
                    all_tests_passed = False
                    continue
                
                csv_data = csv_response.json()
                
                # Verify base64 content
                if 'content' not in csv_data or not csv_data['content']:
                    self.log_test(f"CSV Export - {section}", False,
                                "No base64 content in response")
                    all_tests_passed = False
                    continue
                
                # Try to decode and validate CSV
                try:
                    decoded_content = base64.b64decode(csv_data['content']).decode('utf-8')
                    csv_reader = csv.reader(io.StringIO(decoded_content))
                    rows = list(csv_reader)
                    
                    if len(rows) < 1:
                        self.log_test(f"CSV Export - {section}", False,
                                    "Empty CSV content")
                        all_tests_passed = False
                        continue
                    
                    self.log_test(f"CSV Export - {section}", True,
                                f"Valid CSV with {len(rows)} rows")
                    
                except Exception as decode_error:
                    self.log_test(f"CSV Export - {section}", False,
                                f"Invalid base64/CSV: {str(decode_error)}")
                    all_tests_passed = False
                
            except Exception as e:
                self.log_test(f"CSV Export - {section}", False, f"Exception: {str(e)}")
                all_tests_passed = False
        
        # Test Chart PNG exports
        chart_tests = [
            {'chart_type': 'histogram', 'columns': ['age']},
            {'chart_type': 'correlation_matrix'},
            {'chart_type': 'scatter_plot', 'columns': ['age', 'salary']},
            {'chart_type': 'box_plot', 'columns': ['performance_score']},
            {'chart_type': 'bar_chart', 'columns': ['department']}
        ]
        
        for chart_test in chart_tests:
            try:
                params = {'chart_type': chart_test['chart_type']}
                if 'columns' in chart_test:
                    params['columns'] = chart_test['columns']
                
                chart_response = self.session.get(
                    f"{BASE_URL}/exports/pipeline/{self.pipeline_id}/export-chart",
                    params=params
                )
                
                if chart_response.status_code != 200:
                    self.log_test(f"Chart Export - {chart_test['chart_type']}", False,
                                f"Failed with status {chart_response.status_code}")
                    all_tests_passed = False
                    continue
                
                chart_data = chart_response.json()
                
                # Verify base64 content
                if 'content' not in chart_data or not chart_data['content']:
                    self.log_test(f"Chart Export - {chart_test['chart_type']}", False,
                                "No base64 content in response")
                    all_tests_passed = False
                    continue
                
                # Verify it's valid base64 and proper size
                try:
                    decoded_img = base64.b64decode(chart_data['content'])
                    
                    if len(decoded_img) < 1000:  # Too small to be a valid image
                        self.log_test(f"Chart Export - {chart_test['chart_type']}", False,
                                    f"Image too small: {len(decoded_img)} bytes")
                        all_tests_passed = False
                        continue
                    
                    # Check PNG header
                    if not decoded_img.startswith(b'\x89PNG'):
                        self.log_test(f"Chart Export - {chart_test['chart_type']}", False,
                                    "Invalid PNG header")
                        all_tests_passed = False
                        continue
                    
                    self.log_test(f"Chart Export - {chart_test['chart_type']}", True,
                                f"Valid PNG image ({len(decoded_img):,} bytes)")
                    
                except Exception as decode_error:
                    self.log_test(f"Chart Export - {chart_test['chart_type']}", False,
                                f"Invalid base64/PNG: {str(decode_error)}")
                    all_tests_passed = False
                
            except Exception as e:
                self.log_test(f"Chart Export - {chart_test['chart_type']}", False, f"Exception: {str(e)}")
                all_tests_passed = False
        
        return all_tests_passed
    
    def run_all_tests(self) -> bool:
        """Run complete test suite"""
        print("🧪 Starting Enhanced Visualization and Export Features Test")
        print("=" * 70)
        
        # Test sequence
        tests = [
            ("Authentication", self.test_authentication),
            ("Create Project & Upload Data", self.test_create_project_and_upload_data),
            ("Pipeline Execution", self.test_pipeline_execution),
            ("Pipeline Results Verification", self.test_pipeline_results_verification),
            ("Export Endpoints", self.test_export_endpoints)
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            print(f"\n🔄 Running {test_name}...")
            
            if not test_func():
                all_passed = False
                print(f"❌ {test_name} FAILED - stopping tests")
                break
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        passed_count = sum(1 for result in self.test_results if result['success'])
        total_count = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['message']:
                print(f"   → {result['message']}")
        
        print(f"\nResults: {passed_count}/{total_count} tests passed")
        
        if all_passed:
            print("🎉 ALL TESTS PASSED! Enhanced visualization features are working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return all_passed


def main():
    """Main test execution"""
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()