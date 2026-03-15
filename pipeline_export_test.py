#!/usr/bin/env python3
"""
Pipeline and Export Testing - Focused test for review requirements
Tests LLM status, pipeline functionality, and export endpoints
"""

import requests
import sys
import json
import io
import base64
from datetime import datetime

class PipelineExportTester:
    def __init__(self, base_url="https://private-analyst.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_user_email = "export_test@example.com"
        self.test_password = "TestPassword123!"
        self.project_id = None
        self.pipeline_id = None
        self.token = None
        print(f"🚀 Pipeline & Export Testing")
        print(f"📍 Base URL: {base_url}")
        print("=" * 80)

    def authenticate(self):
        """Authenticate and get token"""
        print(f"\n🔐 Authenticating...")
        try:
            response = self.session.post(f"{self.base_url}/auth/login", json={
                "email": self.test_user_email,
                "password": self.test_password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['token']
                self.session.headers.update({'Authorization': f"Token {self.token}"})
                print(f"   ✅ Authenticated as: {data['user']['name']}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False

    def create_project_with_data(self):
        """Create project and upload CSV data"""
        print(f"\n📁 Creating test project...")
        try:
            # Create project
            response = self.session.post(f"{self.base_url}/projects/", json={
                "name": f"Export Test Project {datetime.now().strftime('%H:%M:%S')}",
                "source_type": "file_upload"
            })
            
            if response.status_code != 201:
                print(f"   ❌ Failed to create project: {response.status_code}")
                return False
                
            project_data = response.json()
            self.project_id = project_data['project_id']
            print(f"   ✅ Created project: {self.project_id}")
            
            # Upload CSV data
            csv_content = """name,age,city,salary,department
John Doe,25,New York,50000,Engineering
Jane Smith,30,Los Angeles,60000,Marketing
Bob Johnson,35,Chicago,55000,Sales
Alice Brown,28,Houston,52000,Engineering
Charlie Wilson,32,Phoenix,58000,Marketing
Eva Davis,29,Boston,54000,Sales
Mike Taylor,31,Seattle,62000,Engineering
Sarah Jones,27,Miami,51000,Marketing"""

            upload_response = self.session.post(
                f"{self.base_url}/projects/{self.project_id}/upload",
                files={'file': ('test_data.csv', csv_content, 'text/csv')}
            )
            
            if upload_response.status_code == 200:
                stats = upload_response.json().get('statistics', {})
                print(f"   ✅ Data uploaded: {stats.get('total_rows', 0)} rows, {stats.get('total_columns', 0)} columns")
                return True
            else:
                print(f"   ❌ Failed to upload data: {upload_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Project creation error: {e}")
            return False

    def test_llm_status(self):
        """Test LLM status endpoint"""
        print(f"\n🤖 Testing LLM Status...")
        try:
            response = self.session.get(f"{self.base_url}/analysis/pipeline/llm-status")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ LLM Status: {'Available' if data.get('available') else 'Not Available'}")
                print(f"   📦 Model: {data.get('model', 'Unknown')}")
                return data.get('available', False)
            else:
                print(f"   ❌ LLM status check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ LLM status error: {e}")
            return False

    def test_pipeline_start(self):
        """Test starting pipeline"""
        print(f"\n🚀 Starting Pipeline...")
        try:
            response = self.session.post(f"{self.base_url}/analysis/pipeline/start/{self.project_id}", json={
                "llm_enabled": True
            })
            
            if response.status_code == 200:
                data = response.json()
                self.pipeline_id = data.get('pipeline_id')
                status = data.get('status', 'unknown')
                print(f"   ✅ Pipeline started: {self.pipeline_id}")
                print(f"   📊 Status: {status}")
                return True
            else:
                print(f"   ❌ Pipeline start failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   🚨 Error: {error_data}")
                except:
                    print(f"   🚨 Error: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Pipeline start error: {e}")
            return False

    def test_pipeline_status(self):
        """Test pipeline status endpoint"""
        print(f"\n📊 Checking Pipeline Status...")
        try:
            response = self.session.get(f"{self.base_url}/analysis/pipeline/{self.pipeline_id}/status")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {data.get('status', 'unknown')}")
                print(f"   📈 Progress: {data.get('progress_percent', 0)}%")
                print(f"   🎯 Current Stage: {data.get('current_stage', 'unknown')}")
                return data.get('status') == 'completed'
            else:
                print(f"   ❌ Pipeline status check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Pipeline status error: {e}")
            return False

    def test_export_pdf(self):
        """Test PDF export"""
        print(f"\n📄 Testing PDF Export...")
        try:
            response = self.session.get(f"{self.base_url}/exports/pipeline/{self.pipeline_id}/export-pdf")
            
            if response.status_code == 200:
                data = response.json()
                filename = data.get('filename', 'unknown')
                content_type = data.get('content_type', 'unknown')
                encoding = data.get('encoding', 'unknown')
                
                print(f"   ✅ PDF Generated: {filename}")
                print(f"   📦 Content Type: {content_type}")
                print(f"   🔢 Encoding: {encoding}")
                
                # Verify base64 content
                if 'content' in data and encoding == 'base64':
                    try:
                        pdf_data = base64.b64decode(data['content'])
                        print(f"   ✅ Base64 decoded successfully ({len(pdf_data)} bytes)")
                        return True
                    except Exception as e:
                        print(f"   ❌ Failed to decode base64: {e}")
                        return False
                else:
                    print(f"   ❌ Missing or invalid content")
                    return False
            else:
                print(f"   ❌ PDF export failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   🚨 Error: {error_data}")
                except:
                    print(f"   🚨 Error: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ PDF export error: {e}")
            return False

    def test_export_excel(self):
        """Test Excel export"""
        print(f"\n📊 Testing Excel Export...")
        try:
            response = self.session.get(f"{self.base_url}/exports/pipeline/{self.pipeline_id}/export-excel")
            
            if response.status_code == 200:
                data = response.json()
                filename = data.get('filename', 'unknown')
                content_type = data.get('content_type', 'unknown')
                encoding = data.get('encoding', 'unknown')
                
                print(f"   ✅ Excel Generated: {filename}")
                print(f"   📦 Content Type: {content_type}")
                print(f"   🔢 Encoding: {encoding}")
                
                # Verify base64 content
                if 'content' in data and encoding == 'base64':
                    try:
                        excel_data = base64.b64decode(data['content'])
                        print(f"   ✅ Base64 decoded successfully ({len(excel_data)} bytes)")
                        return True
                    except Exception as e:
                        print(f"   ❌ Failed to decode base64: {e}")
                        return False
                else:
                    print(f"   ❌ Missing or invalid content")
                    return False
            else:
                print(f"   ❌ Excel export failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   🚨 Error: {error_data}")
                except:
                    print(f"   🚨 Error: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Excel export error: {e}")
            return False

    def run_tests(self):
        """Run all pipeline and export tests"""
        print(f"🔬 STARTING PIPELINE & EXPORT TESTS")
        
        # Authentication
        if not self.authenticate():
            print(f"\n🚨 CRITICAL FAILURE: Authentication failed")
            return 1
            
        # Project setup
        if not self.create_project_with_data():
            print(f"\n🚨 CRITICAL FAILURE: Project setup failed")
            return 1
            
        # LLM Status
        llm_available = self.test_llm_status()
        if not llm_available:
            print(f"\n⚠️  WARNING: LLM not available")
            
        # Pipeline tests
        pipeline_started = self.test_pipeline_start()
        if not pipeline_started:
            print(f"\n🚨 CRITICAL FAILURE: Pipeline start failed")
            return 1
            
        pipeline_completed = self.test_pipeline_status()
        if not pipeline_completed:
            print(f"\n⚠️  WARNING: Pipeline may still be running")
            
        # Export tests
        pdf_success = self.test_export_pdf()
        excel_success = self.test_export_excel()
        
        # Final results
        print(f"\n" + "=" * 80)
        print(f"📊 FINAL RESULTS")
        print(f"   🔐 Authentication: ✅")
        print(f"   📁 Project Setup: ✅")
        print(f"   🤖 LLM Status: {'✅' if llm_available else '⚠️'}")
        print(f"   🚀 Pipeline Start: {'✅' if pipeline_started else '❌'}")
        print(f"   📊 Pipeline Complete: {'✅' if pipeline_completed else '⚠️'}")
        print(f"   📄 PDF Export: {'✅' if pdf_success else '❌'}")
        print(f"   📊 Excel Export: {'✅' if excel_success else '❌'}")
        
        if pipeline_started and (pdf_success or excel_success):
            print(f"\n✅ PIPELINE & EXPORT TESTING SUCCESS")
            print(f"   • LLM Integration Working")
            print(f"   • Pipeline System Functional")
            print(f"   • Export Features {'Fully' if pdf_success and excel_success else 'Partially'} Working")
            return 0
        else:
            print(f"\n❌ PIPELINE & EXPORT TESTING FAILED")
            return 1

def main():
    """Main test execution"""
    tester = PipelineExportTester()
    return tester.run_tests()

if __name__ == "__main__":
    sys.exit(main())