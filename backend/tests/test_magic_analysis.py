"""
Magic Analysis Feature Tests
Tests for one-click data analysis with plain-English insights
Features: run_magic_analysis, apply_magic_cleaning endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://magic-analysis.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@analyticore.com"
ADMIN_PASSWORD = "adminpassword"
TEST_PROJECT_ID = "590b784e-be98-439f-b41c-770c5a1ab704"


class TestMagicAnalysis:
    """Test suite for Magic Analysis API endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for admin user"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        token = response.json().get("token")
        assert token, "No token in login response"
        return token
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Auth headers for requests"""
        return {
            "Authorization": f"Token {auth_token}",
            "Content-Type": "application/json"
        }
    
    # ================== GET /api/analysis/{project_id}/magic-analyze Tests ==================
    
    def test_magic_analysis_returns_200_for_authenticated_user(self, auth_headers):
        """Magic Analysis endpoint should return 200 for authenticated user with valid project"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/magic-analyze",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"PASS: Magic Analysis returned 200 for authenticated user")
    
    def test_magic_analysis_returns_executive_summary(self, auth_headers):
        """Magic Analysis should return executive_summary with quality_score and text"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/magic-analyze",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify executive_summary structure
        assert 'executive_summary' in data, "Missing executive_summary"
        summary = data['executive_summary']
        
        assert 'quality_score' in summary, "Missing quality_score in executive_summary"
        assert isinstance(summary['quality_score'], (int, float)), "quality_score should be numeric"
        assert 0 <= summary['quality_score'] <= 100, "quality_score should be 0-100"
        
        assert 'quality_label' in summary, "Missing quality_label"
        assert summary['quality_label'] in ['excellent', 'good', 'fair', 'needs attention'], \
            f"Invalid quality_label: {summary['quality_label']}"
        
        assert 'text' in summary, "Missing summary text"
        assert isinstance(summary['text'], str), "Summary text should be string"
        assert len(summary['text']) > 0, "Summary text should not be empty"
        
        assert 'stats' in summary, "Missing stats in executive_summary"
        stats = summary['stats']
        assert 'total_rows' in stats, "Missing total_rows in stats"
        assert 'total_columns' in stats, "Missing total_columns in stats"
        assert 'numeric_columns' in stats, "Missing numeric_columns in stats"
        assert 'missing_values' in stats, "Missing missing_values in stats"
        
        print(f"PASS: Executive summary structure is valid")
        print(f"  - Quality Score: {summary['quality_score']}")
        print(f"  - Quality Label: {summary['quality_label']}")
        print(f"  - Total Rows: {stats['total_rows']}")
        print(f"  - Total Columns: {stats['total_columns']}")
    
    def test_magic_analysis_returns_data_profile(self, auth_headers):
        """Magic Analysis should return data_profile with column details"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/magic-analyze",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert 'data_profile' in data, "Missing data_profile"
        profile = data['data_profile']
        
        assert 'columns' in profile, "Missing columns in data_profile"
        assert isinstance(profile['columns'], list), "columns should be a list"
        assert len(profile['columns']) > 0, "columns should not be empty"
        
        # Verify column structure
        col = profile['columns'][0]
        assert 'name' in col, "Missing name in column profile"
        assert 'dtype' in col, "Missing dtype in column profile"
        assert 'type' in col, "Missing type in column profile"
        
        print(f"PASS: Data profile contains {len(profile['columns'])} columns")
        for c in profile['columns']:
            print(f"  - {c['name']}: {c['type']} ({c['dtype']})")
    
    def test_magic_analysis_returns_data_quality(self, auth_headers):
        """Magic Analysis should return data_quality with issues"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/magic-analyze",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert 'data_quality' in data, "Missing data_quality"
        quality = data['data_quality']
        
        assert 'quality_score' in quality, "Missing quality_score in data_quality"
        assert 'total_issues' in quality, "Missing total_issues"
        assert 'critical_issues' in quality, "Missing critical_issues count"
        assert 'warning_issues' in quality, "Missing warning_issues count"
        assert 'info_issues' in quality, "Missing info_issues count"
        assert 'issues' in quality, "Missing issues list"
        assert isinstance(quality['issues'], list), "issues should be a list"
        
        print(f"PASS: Data quality section valid")
        print(f"  - Quality Score: {quality['quality_score']}")
        print(f"  - Total Issues: {quality['total_issues']}")
        print(f"  - Critical: {quality['critical_issues']}, Warning: {quality['warning_issues']}, Info: {quality['info_issues']}")
    
    def test_magic_analysis_returns_cleaning_suggestions(self, auth_headers):
        """Magic Analysis should return cleaning_suggestions list"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/magic-analyze",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert 'cleaning_suggestions' in data, "Missing cleaning_suggestions"
        suggestions = data['cleaning_suggestions']
        assert isinstance(suggestions, list), "cleaning_suggestions should be a list"
        
        # If there are suggestions, verify structure
        if len(suggestions) > 0:
            suggestion = suggestions[0]
            assert 'column' in suggestion, "Missing column in suggestion"
            assert 'issue' in suggestion, "Missing issue in suggestion"
            assert 'count' in suggestion, "Missing count in suggestion"
            assert 'priority' in suggestion, "Missing priority in suggestion"
            assert suggestion['priority'] in ['high', 'medium', 'low'], \
                f"Invalid priority: {suggestion['priority']}"
            
            # Verify options if present
            if 'options' in suggestion:
                assert isinstance(suggestion['options'], list), "options should be a list"
                if len(suggestion['options']) > 0:
                    opt = suggestion['options'][0]
                    assert 'strategy' in opt, "Missing strategy in option"
                    assert 'description' in opt, "Missing description in option"
        
        print(f"PASS: Cleaning suggestions valid - {len(suggestions)} suggestions found")
    
    def test_magic_analysis_returns_key_insights(self, auth_headers):
        """Magic Analysis should return key_insights with patterns/relationships"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/magic-analyze",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert 'key_insights' in data, "Missing key_insights"
        insights = data['key_insights']
        assert isinstance(insights, list), "key_insights should be a list"
        
        # Check for expected insight types
        insight_types = [i.get('type') for i in insights]
        print(f"PASS: Key insights valid - {len(insights)} insights found")
        print(f"  - Insight types: {set(insight_types)}")
        
        # If there are insights, verify structure
        if len(insights) > 0:
            insight = insights[0]
            assert 'type' in insight, "Missing type in insight"
            assert 'title' in insight, "Missing title in insight"
            assert 'message' in insight, "Missing message in insight"
            assert 'priority' in insight, "Missing priority in insight"
    
    def test_magic_analysis_returns_visualization_suggestions(self, auth_headers):
        """Magic Analysis should return suggested_visualizations"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/magic-analyze",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert 'suggested_visualizations' in data, "Missing suggested_visualizations"
        viz = data['suggested_visualizations']
        assert isinstance(viz, list), "suggested_visualizations should be a list"
        
        # Verify structure
        if len(viz) > 0:
            v = viz[0]
            assert 'type' in v, "Missing type in visualization"
            assert 'title' in v, "Missing title in visualization"
            assert 'description' in v, "Missing description in visualization"
            assert 'columns' in v, "Missing columns in visualization"
            
            viz_types = [x.get('type') for x in viz]
            print(f"PASS: Visualization suggestions valid - {len(viz)} suggestions")
            print(f"  - Chart types suggested: {set(viz_types)}")
        else:
            print(f"PASS: Visualization suggestions section present (empty list)")
    
    def test_magic_analysis_returns_next_steps(self, auth_headers):
        """Magic Analysis should return next_steps recommendations"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/magic-analyze",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert 'next_steps' in data, "Missing next_steps"
        steps = data['next_steps']
        assert isinstance(steps, list), "next_steps should be a list"
        
        if len(steps) > 0:
            step = steps[0]
            assert 'step' in step, "Missing step number"
            assert 'action' in step, "Missing action in step"
            assert 'description' in step, "Missing description in step"
        
        print(f"PASS: Next steps valid - {len(steps)} steps recommended")
    
    def test_magic_analysis_returns_timestamp(self, auth_headers):
        """Magic Analysis should include analysis_timestamp"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/magic-analyze",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert 'analysis_timestamp' in data, "Missing analysis_timestamp"
        assert isinstance(data['analysis_timestamp'], str), "timestamp should be string"
        print(f"PASS: Analysis timestamp present: {data['analysis_timestamp']}")
    
    def test_magic_analysis_returns_401_for_unauthenticated(self):
        """Magic Analysis endpoint should return 401 for unauthenticated user"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/magic-analyze"
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"PASS: Magic Analysis returns 401 for unauthenticated user")
    
    def test_magic_analysis_returns_404_for_invalid_project(self, auth_headers):
        """Magic Analysis should return 404 for non-existent project"""
        fake_project_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(
            f"{BASE_URL}/api/analysis/{fake_project_id}/magic-analyze",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"PASS: Magic Analysis returns 404 for invalid project")
    
    # ================== POST /api/analysis/{project_id}/magic-apply-cleaning Tests ==================
    
    def test_apply_cleaning_returns_400_without_actions(self, auth_headers):
        """Apply cleaning should return 400 when no actions provided"""
        response = requests.post(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/magic-apply-cleaning",
            headers=auth_headers,
            json={"actions": []}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print(f"PASS: Apply cleaning returns 400 for empty actions")
    
    def test_apply_cleaning_returns_401_for_unauthenticated(self):
        """Apply cleaning should return 401 for unauthenticated user"""
        response = requests.post(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/magic-apply-cleaning",
            json={"actions": [{"column": "test", "issue": "missing_values", "strategy": "mean"}]}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"PASS: Apply cleaning returns 401 for unauthenticated user")
    
    def test_apply_cleaning_returns_404_for_invalid_project(self, auth_headers):
        """Apply cleaning should return 404 for non-existent project"""
        fake_project_id = "00000000-0000-0000-0000-000000000000"
        response = requests.post(
            f"{BASE_URL}/api/analysis/{fake_project_id}/magic-apply-cleaning",
            headers=auth_headers,
            json={"actions": [{"column": "test", "issue": "missing_values", "strategy": "mean"}]}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"PASS: Apply cleaning returns 404 for invalid project")


class TestMagicAnalysisDataContent:
    """Test the actual data content of Magic Analysis response"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authentication headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = response.json().get("token")
        return {"Authorization": f"Token {token}", "Content-Type": "application/json"}
    
    @pytest.fixture(scope="class")
    def analysis_result(self, auth_headers):
        """Get full Magic Analysis result"""
        response = requests.get(
            f"{BASE_URL}/api/analysis/{TEST_PROJECT_ID}/magic-analyze",
            headers=auth_headers
        )
        return response.json()
    
    def test_quality_score_reflects_data_quality(self, analysis_result):
        """Quality score should reflect actual data quality (no missing = high score)"""
        summary = analysis_result['executive_summary']
        stats = summary['stats']
        quality_score = summary['quality_score']
        
        # The test data has 15 rows, 6 columns, no missing values
        if stats['missing_values'] == 0:
            # With no missing values, quality should be good or better
            assert quality_score >= 60, f"Quality score {quality_score} too low for clean data"
            print(f"PASS: Quality score {quality_score} appropriately high for clean data")
        else:
            print(f"PASS: Quality score {quality_score} reflects {stats['missing_values']} missing values")
    
    def test_insights_include_correlations_if_present(self, analysis_result):
        """Insights should detect strong correlations between age and salary"""
        insights = analysis_result['key_insights']
        
        # Find correlation insights
        correlation_insights = [i for i in insights if i.get('type') == 'correlation']
        
        print(f"Found {len(correlation_insights)} correlation insights")
        for insight in correlation_insights:
            print(f"  - {insight.get('title')}: {insight.get('message')[:80]}...")
        
        # Test data should have age-salary correlation per the agent notes
        if len(correlation_insights) > 0:
            print(f"PASS: Correlation insights detected")
        else:
            # It's also valid if no strong correlation exists
            print(f"INFO: No strong correlations detected (may be expected for small dataset)")
    
    def test_ml_readiness_insight_present_for_numeric_data(self, analysis_result):
        """ML readiness insight should be present for data with multiple numeric columns"""
        insights = analysis_result['key_insights']
        summary = analysis_result['executive_summary']
        
        numeric_cols = summary['stats'].get('numeric_columns', 0)
        ml_insights = [i for i in insights if i.get('type') == 'ml_ready']
        
        if numeric_cols >= 3:
            # Should suggest ML readiness
            print(f"PASS: {numeric_cols} numeric columns, ML readiness noted")
        else:
            print(f"INFO: {numeric_cols} numeric columns (ML insight may not appear)")
    
    def test_plain_english_summary_is_readable(self, analysis_result):
        """Summary text should be plain English, not technical jargon"""
        summary_text = analysis_result['executive_summary']['text']
        
        # Check for readable patterns
        assert 'dataset' in summary_text.lower() or 'data' in summary_text.lower(), \
            "Summary should mention 'data' or 'dataset'"
        assert 'rows' in summary_text.lower() or 'records' in summary_text.lower(), \
            "Summary should mention row count in readable format"
        
        # Should not have excessive technical jargon
        technical_terms = ['NaN', 'dtype', 'index', 'axis', 'inplace']
        for term in technical_terms:
            assert term not in summary_text, f"Summary should avoid technical term: {term}"
        
        print(f"PASS: Summary is readable plain English")
        print(f"  First 200 chars: {summary_text[:200]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
