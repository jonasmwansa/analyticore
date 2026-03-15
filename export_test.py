#!/usr/bin/env python3
"""
Simplified Backend Test for Enhanced Export Features
Tests export endpoints using existing completed pipelines.
"""
import requests
import json
import base64
import csv
import io
import time
import os
import sys

# Configuration
BASE_URL = "https://private-analyst.preview.emergentagent.com/api"
TEST_EMAIL = "verified_test@example.com"
TEST_PASSWORD = "TestPassword123!"

def main():
    """Test export functionality directly"""
    print("🧪 Testing Enhanced Export Features")
    print("=" * 50)
    
    session = requests.Session()
    
    # Login
    print("🔄 Logging in...")
    login_response = session.post(f"{BASE_URL}/auth/login", 
                                json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["token"]
    session.headers.update({"Authorization": f"Token {token}"})
    print("✅ Login successful")
    
    # Find a completed pipeline
    print("🔄 Looking for completed pipelines...")
    
    # Try the known pipeline ID from our previous test
    test_pipeline_ids = [
        "92abec8d-16f2-49e4-864f-00397105f388", 
        "72307e31-6e0a-4bbc-aa47-e8461542a3f7"
    ]
    
    completed_pipeline = None
    for pipeline_id in test_pipeline_ids:
        try:
            status_response = session.get(f"{BASE_URL}/analysis/pipeline/{pipeline_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data.get("status") == "completed":
                    completed_pipeline = pipeline_id
                    print(f"✅ Found completed pipeline: {pipeline_id}")
                    break
                else:
                    print(f"🔄 Pipeline {pipeline_id}: {status_data.get('status')} ({status_data.get('progress_percent', 0)}%)")
        except Exception as e:
            continue
    
    if not completed_pipeline:
        print("❌ No completed pipeline found for testing")
        print("⚠️  The enhanced pipeline features may still be running")
        return False
    
    # Test export endpoints
    print(f"\n🧪 Testing export endpoints with pipeline: {completed_pipeline}")
    
    success_count = 0
    total_tests = 0
    
    # Test CSV exports
    csv_sections = ["statistics", "visualizations", "correlation", "cleaning", "insights", "summary"]
    for section in csv_sections:
        total_tests += 1
        try:
            csv_response = session.get(
                f"{BASE_URL}/exports/pipeline/{completed_pipeline}/export-csv",
                params={"section": section}
            )
            
            if csv_response.status_code == 200:
                csv_data = csv_response.json()
                if "content" in csv_data and csv_data["content"]:
                    # Try to decode CSV
                    decoded_content = base64.b64decode(csv_data["content"]).decode("utf-8")
                    csv_reader = csv.reader(io.StringIO(decoded_content))
                    rows = list(csv_reader)
                    print(f"✅ CSV Export ({section}): {len(rows)} rows")
                    success_count += 1
                else:
                    print(f"❌ CSV Export ({section}): No content")
            else:
                print(f"❌ CSV Export ({section}): HTTP {csv_response.status_code}")
        except Exception as e:
            print(f"❌ CSV Export ({section}): Exception - {str(e)[:50]}")
    
    # Test chart PNG exports
    chart_tests = [
        {"chart_type": "histogram", "columns": ["age"]},
        {"chart_type": "correlation_matrix"},
        {"chart_type": "scatter_plot", "columns": ["age", "salary"]},
        {"chart_type": "box_plot", "columns": ["performance_score"]},
    ]
    
    for chart_test in chart_tests:
        total_tests += 1
        try:
            params = {"chart_type": chart_test["chart_type"]}
            if "columns" in chart_test:
                params["columns"] = chart_test["columns"]
            
            chart_response = session.get(
                f"{BASE_URL}/exports/pipeline/{completed_pipeline}/export-chart",
                params=params
            )
            
            if chart_response.status_code == 200:
                chart_data = chart_response.json()
                if "content" in chart_data and chart_data["content"]:
                    decoded_img = base64.b64decode(chart_data["content"])
                    if len(decoded_img) > 1000 and decoded_img.startswith(b"\x89PNG"):
                        print(f"✅ Chart Export ({chart_test['chart_type']}): {len(decoded_img):,} bytes PNG")
                        success_count += 1
                    else:
                        print(f"❌ Chart Export ({chart_test['chart_type']}): Invalid PNG")
                else:
                    print(f"❌ Chart Export ({chart_test['chart_type']}): No content")
            else:
                print(f"❌ Chart Export ({chart_test['chart_type']}): HTTP {chart_response.status_code}")
        except Exception as e:
            print(f"❌ Chart Export ({chart_test['chart_type']}): Exception - {str(e)[:50]}")
    
    # Test pipeline results verification
    total_tests += 1
    try:
        results_response = session.get(f"{BASE_URL}/analysis/pipeline/{completed_pipeline}/results")
        
        if results_response.status_code == 200:
            results = results_response.json()
            
            # Check for enhanced visualization features
            visualization = results.get("visualization", {})
            smart_recs = visualization.get("smart_recommendations", {})
            recommendations = smart_recs.get("recommendations", [])
            column_profiles = visualization.get("column_profiles", {}) or smart_recs.get("column_profiles", {})
            llm_chart_insights = visualization.get("llm_chart_insights", {})
            
            checks = [
                (len(recommendations) > 0, f"Smart recommendations: {len(recommendations)} found"),
                (len(column_profiles) > 0, f"Column profiles: {len(column_profiles)} columns"),
                (len(llm_chart_insights) > 0, f"LLM chart insights: {len(llm_chart_insights)} insights"),
            ]
            
            all_passed = True
            for passed, message in checks:
                if passed:
                    print(f"✅ {message}")
                else:
                    print(f"❌ {message}")
                    all_passed = False
            
            if all_passed:
                success_count += 1
                print("✅ Pipeline Results: Enhanced features present")
            else:
                print("❌ Pipeline Results: Missing enhanced features")
        else:
            print(f"❌ Pipeline Results: HTTP {results_response.status_code}")
    except Exception as e:
        print(f"❌ Pipeline Results: Exception - {str(e)[:50]}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 ALL ENHANCED EXPORT TESTS PASSED!")
        return True
    else:
        print("⚠️  Some export tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)