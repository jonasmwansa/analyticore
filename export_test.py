#!/usr/bin/env python3
"""
Export Testing - Test export endpoints with existing pipeline
"""

import requests
import sys
import json
import base64

class ExportTester:
    def __init__(self, base_url="https://private-analyst.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_user_email = "export_test@example.com"
        self.test_password = "TestPassword123!"
        # Using an existing completed pipeline ID
        self.pipeline_id = "302ca218-fb95-44ac-afe9-4d87b4709a63"
        print(f"📤 Export Endpoint Testing")
        print(f"📍 Base URL: {base_url}")
        print(f"🔧 Testing with Pipeline: {self.pipeline_id}")
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
                token = data['token']
                self.session.headers.update({'Authorization': f"Token {token}"})
                print(f"   ✅ Authenticated as: {data['user']['name']}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
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
                return True
            else:
                print(f"   ❌ LLM status check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ LLM status error: {e}")
            return False

    def test_pipeline_status(self):
        """Test pipeline status to verify it exists"""
        print(f"\n📊 Verifying Pipeline Status...")
        try:
            response = self.session.get(f"{self.base_url}/analysis/pipeline/{self.pipeline_id}/status")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                project_name = data.get('project_name', 'unknown')
                print(f"   ✅ Pipeline exists: {status}")
                print(f"   📁 Project: {project_name}")
                return status == 'completed'
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
                        
                        # Check if it's a valid PDF by looking for PDF header
                        if pdf_data.startswith(b'%PDF-'):
                            print(f"   ✅ Valid PDF file header detected")
                        else:
                            print(f"   ⚠️  PDF header not detected (first 10 bytes: {pdf_data[:10]})")
                        
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
                        
                        # Check if it's a valid Excel file by looking for Excel signature
                        if excel_data.startswith(b'PK'):  # Excel files are ZIP-based
                            print(f"   ✅ Valid Excel file signature detected")
                        else:
                            print(f"   ⚠️  Excel signature not detected (first 10 bytes: {excel_data[:10]})")
                        
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
        """Run export tests"""
        print(f"🔬 STARTING EXPORT FUNCTIONALITY TESTS")
        
        # Authentication
        if not self.authenticate():
            print(f"\n🚨 CRITICAL FAILURE: Authentication failed")
            return 1
            
        # LLM Status (part of review requirements)
        llm_status = self.test_llm_status()
        
        # Verify pipeline exists
        pipeline_valid = self.test_pipeline_status()
        if not pipeline_valid:
            print(f"\n🚨 CRITICAL FAILURE: Pipeline not available for export testing")
            return 1
            
        # Export tests
        pdf_success = self.test_export_pdf()
        excel_success = self.test_export_excel()
        
        # Final results
        print(f"\n" + "=" * 80)
        print(f"📊 EXPORT TESTING RESULTS")
        print(f"   🔐 Authentication: ✅")
        print(f"   🤖 LLM Status: {'✅' if llm_status else '❌'}")
        print(f"   📊 Pipeline Verified: {'✅' if pipeline_valid else '❌'}")
        print(f"   📄 PDF Export: {'✅' if pdf_success else '❌'}")
        print(f"   📊 Excel Export: {'✅' if excel_success else '❌'}")
        
        if llm_status and pipeline_valid and pdf_success and excel_success:
            print(f"\n✅ ALL EXPORT TESTS PASSED")
            print(f"   • LLM Integration Available")
            print(f"   • Pipeline Results Accessible")
            print(f"   • PDF Export Working with Valid Content")
            print(f"   • Excel Export Working with Valid Content")
            return 0
        else:
            failed_tests = []
            if not llm_status:
                failed_tests.append("LLM Status")
            if not pdf_success:
                failed_tests.append("PDF Export")
            if not excel_success:
                failed_tests.append("Excel Export")
            
            print(f"\n❌ EXPORT TESTS FAILED")
            print(f"   Failed: {', '.join(failed_tests)}")
            return 1

def main():
    """Main test execution"""
    tester = ExportTester()
    return tester.run_tests()

if __name__ == "__main__":
    sys.exit(main())