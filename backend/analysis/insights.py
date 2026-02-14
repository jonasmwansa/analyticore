"""
AI Insights Generator for AnalytiCore
Generates natural language summaries and actionable recommendations
"""

from django.conf import settings
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio
import json


class InsightsGenerator:
    """Generates AI-powered insights from data analysis"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.chat = LlmChat(
            api_key=settings.EMERGENT_LLM_KEY,
            session_id=f"insights_{project_id}",
            system_message="""You are a data analyst expert. Your job is to provide clear, actionable insights from data analysis results. 
Be concise but comprehensive. Focus on:
1. Key findings that matter for decision-making
2. Potential data quality issues
3. Interesting patterns or correlations
4. Recommendations for data cleaning and transformation

Always respond in valid JSON format when asked."""
        )
        self.chat.with_model("openai", "gpt-5.2")
    
    def generate_quick_insights(self, statistics: dict, correlation: dict = None) -> dict:
        """Generate a natural language summary of the data analysis"""
        
        summary = statistics.get('summary', {})
        numeric_stats = statistics.get('numeric', {})
        categorical_stats = statistics.get('categorical', {})
        
        # Build context for AI
        context = f"""
Analyze this dataset and provide key insights:

**Dataset Overview:**
- Total Rows: {summary.get('total_rows', 'N/A')}
- Total Columns: {summary.get('total_columns', 'N/A')}
- Numeric Columns: {summary.get('numeric_columns', 0)}
- Categorical Columns: {summary.get('categorical_columns', 0)}
- Total Missing Values: {summary.get('total_missing', 0)}
- Duplicate Rows: {summary.get('total_duplicates', 0)}

**Numeric Column Statistics:**
"""
        for col, stats in numeric_stats.items():
            context += f"\n{col}:\n"
            context += f"  - Mean: {stats.get('mean')}, Median: {stats.get('50%')}, Std: {stats.get('std')}\n"
            context += f"  - Range: {stats.get('min')} to {stats.get('max')}\n"
            context += f"  - Missing: {stats.get('missing')} ({stats.get('missing_pct', 0)}%)\n"
            if stats.get('skewness'):
                context += f"  - Skewness: {stats.get('skewness')}, Kurtosis: {stats.get('kurtosis')}\n"

        if categorical_stats:
            context += "\n**Categorical Column Statistics:**\n"
            for col, stats in categorical_stats.items():
                context += f"\n{col}:\n"
                context += f"  - Unique Values: {stats.get('unique')}\n"
                context += f"  - Most Common: {stats.get('top')} (appears {stats.get('freq')} times)\n"
                context += f"  - Missing: {stats.get('missing')} ({stats.get('missing_pct', 0)}%)\n"

        if correlation and correlation.get('top_correlations'):
            context += "\n**Top Correlations:**\n"
            for corr in correlation.get('top_correlations', [])[:5]:
                context += f"  - {corr['column1']} vs {corr['column2']}: {corr['correlation']} ({corr['strength']})\n"

        context += """
Please provide your analysis in this JSON format:
{
    "executive_summary": "A 2-3 sentence overview of the most important findings",
    "key_findings": [
        {"finding": "description", "importance": "high/medium/low"},
        ...
    ],
    "data_quality_issues": [
        {"issue": "description", "severity": "critical/warning/info", "affected_columns": ["col1", "col2"]},
        ...
    ],
    "patterns_discovered": [
        {"pattern": "description", "columns_involved": ["col1", "col2"]},
        ...
    ],
    "recommendations": [
        {"action": "what to do", "priority": "high/medium/low", "reason": "why"},
        ...
    ]
}

Return ONLY valid JSON, no additional text.
"""
        
        message = UserMessage(text=context)
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self.chat.send_message(message))
            loop.close()
            
            # Parse response
            try:
                insights = json.loads(response)
            except:
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean[7:]
                if response_clean.endswith('```'):
                    response_clean = response_clean[:-3]
                insights = json.loads(response_clean.strip())
            
            return insights
        except Exception as e:
            return {
                "executive_summary": f"Unable to generate AI insights: {str(e)}",
                "key_findings": [],
                "data_quality_issues": [],
                "patterns_discovered": [],
                "recommendations": []
            }
    
    def generate_column_actions(self, column_name: str, column_stats: dict, column_type: str) -> dict:
        """Generate recommended actions for a specific column"""
        
        actions = {
            "column": column_name,
            "type": column_type,
            "issues_detected": [],
            "recommended_actions": []
        }
        
        # Check for missing values
        missing_pct = column_stats.get('missing_pct', 0)
        if missing_pct > 0:
            severity = 'critical' if missing_pct > 20 else ('warning' if missing_pct > 5 else 'info')
            actions['issues_detected'].append({
                "type": "missing_values",
                "description": f"{column_stats.get('missing', 0)} missing values ({missing_pct}%)",
                "severity": severity
            })
            
            # Add recommended actions based on type
            if column_type == 'numeric':
                actions['recommended_actions'].append({
                    "action": "fill_missing",
                    "label": "Fill with Mean",
                    "strategy": "mean",
                    "description": f"Replace missing values with column mean ({column_stats.get('mean', 0):.2f})"
                })
                actions['recommended_actions'].append({
                    "action": "fill_missing",
                    "label": "Fill with Median",
                    "strategy": "median",
                    "description": f"Replace missing values with column median ({column_stats.get('50%', 0):.2f})"
                })
            else:
                actions['recommended_actions'].append({
                    "action": "fill_missing",
                    "label": "Fill with Mode",
                    "strategy": "mode",
                    "description": f"Replace missing values with most common value ({column_stats.get('top', 'N/A')})"
                })
            
            actions['recommended_actions'].append({
                "action": "drop_rows",
                "label": "Drop Rows with Missing",
                "strategy": "drop",
                "description": f"Remove {column_stats.get('missing', 0)} rows with missing values"
            })
        
        # Check for outliers (numeric only)
        if column_type == 'numeric':
            skewness = column_stats.get('skewness')
            if skewness and abs(skewness) > 1:
                actions['issues_detected'].append({
                    "type": "skewed_distribution",
                    "description": f"{'Right' if skewness > 0 else 'Left'}-skewed distribution (skewness: {skewness:.2f})",
                    "severity": "warning"
                })
            
            # Check IQR-based outliers
            if column_stats.get('iqr'):
                q1 = column_stats.get('25%', 0)
                q3 = column_stats.get('75%', 0)
                iqr = column_stats.get('iqr', 0)
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                if column_stats.get('min', 0) < lower_bound or column_stats.get('max', 0) > upper_bound:
                    actions['issues_detected'].append({
                        "type": "outliers",
                        "description": f"Potential outliers detected outside range [{lower_bound:.2f}, {upper_bound:.2f}]",
                        "severity": "warning"
                    })
                    
                    actions['recommended_actions'].append({
                        "action": "remove_outliers",
                        "label": "Remove Outliers (IQR)",
                        "strategy": "iqr",
                        "description": f"Remove values outside 1.5 * IQR range"
                    })
                    actions['recommended_actions'].append({
                        "action": "cap_outliers",
                        "label": "Cap Outliers",
                        "strategy": "cap",
                        "description": f"Cap values to [{lower_bound:.2f}, {upper_bound:.2f}]"
                    })
        
        # Check for potential type conversion
        if column_type == 'categorical':
            unique_count = column_stats.get('unique', 0)
            total_count = column_stats.get('count', 1)
            
            # High cardinality warning
            if unique_count > 100:
                actions['issues_detected'].append({
                    "type": "high_cardinality",
                    "description": f"High cardinality: {unique_count} unique values",
                    "severity": "info"
                })
            
            # Might be numeric stored as text
            if unique_count / total_count > 0.8:
                actions['recommended_actions'].append({
                    "action": "convert_type",
                    "label": "Convert to Numeric",
                    "target_type": "numeric",
                    "description": "High uniqueness ratio - might be numeric values stored as text"
                })
        
        # Text cleaning options
        if column_type in ['categorical', 'text']:
            actions['recommended_actions'].append({
                "action": "text_transform",
                "label": "Trim Whitespace",
                "strategy": "trim",
                "description": "Remove leading/trailing whitespace"
            })
            actions['recommended_actions'].append({
                "action": "text_transform",
                "label": "Convert to Lowercase",
                "strategy": "lowercase",
                "description": "Standardize text to lowercase"
            })
        
        # Date conversion suggestion
        if column_type == 'datetime' or (column_type == 'categorical' and column_stats.get('unique', 0) > 10):
            actions['recommended_actions'].append({
                "action": "convert_type",
                "label": "Convert to DateTime",
                "target_type": "datetime",
                "description": "Parse as date/time values"
            })
        
        return actions


def get_all_column_actions(statistics: dict) -> list:
    """Generate actions for all columns in the dataset"""
    
    all_actions = []
    
    # Process numeric columns
    for col, stats in statistics.get('numeric', {}).items():
        generator = InsightsGenerator("temp")
        actions = generator.generate_column_actions(col, stats, 'numeric')
        all_actions.append(actions)
    
    # Process categorical columns
    for col, stats in statistics.get('categorical', {}).items():
        generator = InsightsGenerator("temp")
        actions = generator.generate_column_actions(col, stats, 'categorical')
        all_actions.append(actions)
    
    # Process datetime columns
    for col, stats in statistics.get('datetime', {}).items():
        generator = InsightsGenerator("temp")
        actions = generator.generate_column_actions(col, stats, 'datetime')
        all_actions.append(actions)
    
    return all_actions
