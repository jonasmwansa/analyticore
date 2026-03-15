"""
Local LLM Service - Provides AI-powered insights using locally running models
No external API calls - Full privacy, data never leaves your system
"""
import json
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Check if ollama is available
OLLAMA_AVAILABLE = False
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    logger.warning("Ollama library not installed. Local LLM features will use rule-based fallbacks.")


class LocalLLMService:
    """
    Service for generating AI-powered insights using local LLM models.
    Falls back to rule-based insights if Ollama is not available.
    """
    
    DEFAULT_MODEL = "qwen2.5:1.5b"
    OLLAMA_HOST = "http://localhost:11434"
    
    def __init__(self, model: str = None):
        self.model = model or self.DEFAULT_MODEL
        self._ollama_ready = None
    
    @property
    def is_available(self) -> bool:
        """Check if local LLM is available and ready"""
        if self._ollama_ready is not None:
            return self._ollama_ready
        
        if not OLLAMA_AVAILABLE:
            self._ollama_ready = False
            return False
        
        try:
            # Test connection to Ollama
            response = ollama.list()
            models = [m.get('name', m.get('model', '')) for m in response.get('models', [])]
            self._ollama_ready = any(self.model.split(':')[0] in m for m in models)
            if not self._ollama_ready:
                logger.warning(f"Model {self.model} not found. Available models: {models}")
            return self._ollama_ready
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            self._ollama_ready = False
            return False
    
    def generate_insight(self, prompt: str, context: Dict = None, max_tokens: int = 500) -> str:
        """Generate insight using local LLM or fallback to rule-based"""
        if not self.is_available:
            return self._rule_based_response(prompt, context)
        
        try:
            system_prompt = """You are a professional data analyst assistant. 
            Provide concise, actionable insights in plain English.
            Focus on business impact and practical recommendations.
            Be specific and quantitative where possible.
            Keep responses under 200 words."""
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            )
            return response.get('message', {}).get('content', '')
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._rule_based_response(prompt, context)
    
    def generate_executive_summary(self, df: pd.DataFrame, statistics: Dict) -> str:
        """Generate executive summary for dataset"""
        context = self._build_data_context(df, statistics)
        
        prompt = f"""Analyze this dataset and provide an executive summary:

Dataset Overview:
- {context['rows']:,} rows, {context['columns']} columns
- Numeric columns: {context['numeric_cols']}
- Categorical columns: {context['categorical_cols']}
- Missing values: {context['missing_pct']:.1f}%
- Duplicate rows: {context['duplicates']}

Key Statistics:
{context['stats_summary']}

Provide a 2-3 paragraph executive summary highlighting:
1. Data quality and completeness
2. Key patterns or anomalies
3. Recommended next steps"""

        return self.generate_insight(prompt, context)
    
    def generate_cleaning_insights(self, df: pd.DataFrame, issues: List[Dict]) -> str:
        """Generate insights about data cleaning needs"""
        context = self._build_data_context(df)
        issues_text = "\n".join([f"- {i.get('message', str(i))}" for i in issues[:10]])
        
        prompt = f"""As a data quality expert, analyze these data issues:

{issues_text}

Dataset has {context['rows']:,} rows and {context['columns']} columns.

Provide recommendations for:
1. Which issues to prioritize
2. Best strategies for handling each issue
3. Potential impact on analysis if left unaddressed"""

        return self.generate_insight(prompt, context)
    
    def generate_correlation_insights(self, correlations: List[Dict]) -> str:
        """Generate insights about correlation patterns"""
        if not correlations:
            return "No significant correlations found in the dataset."
        
        corr_text = "\n".join([
            f"- {c['column1']} vs {c['column2']}: {c['correlation']:.3f} ({c.get('strength', 'moderate')})"
            for c in correlations[:10]
        ])
        
        prompt = f"""Analyze these correlation findings:

{corr_text}

Explain:
1. What these relationships suggest about the data
2. Which correlations are most actionable
3. Caution points for interpretation (spurious correlations, confounding)"""

        return self.generate_insight(prompt, {"correlations": correlations})
    
    def generate_visualization_recommendations(self, df: pd.DataFrame, insights: List[Dict]) -> str:
        """Generate visualization recommendations"""
        context = self._build_data_context(df)
        insights_text = "\n".join([f"- {i.get('title', '')}: {i.get('message', '')}" for i in insights[:5]])
        
        prompt = f"""Given this data profile:
- {context['numeric_cols']} numeric columns
- {context['categorical_cols']} categorical columns
- Key insights: {insights_text}

Recommend the top 3 visualizations for:
1. Communicating findings to executives
2. Exploring relationships in the data
3. Identifying outliers or anomalies"""

        return self.generate_insight(prompt, context)
    
    def generate_chart_narrative(self, chart_type: str, columns: List[str], 
                                  data_summary: Dict, chart_config: Dict = None) -> str:
        """Generate a dynamic narrative for a specific chart"""
        prompt = f"""You are creating a narrative for a {chart_type} visualization.

Chart Details:
- Type: {chart_type}
- Columns: {', '.join(columns)}
- Data Summary: {data_summary}

Generate a concise, insightful narrative (2-3 sentences) that:
1. Describes what the chart shows
2. Highlights the key finding or pattern
3. Suggests what action to take based on this insight

Be specific to the actual data values provided."""

        return self.generate_insight(prompt, {'chart_type': chart_type, 'columns': columns})
    
    def generate_anomaly_narrative(self, column: str, anomalies: List[Dict], 
                                   stats: Dict) -> str:
        """Generate narrative about detected anomalies"""
        anomaly_text = "\n".join([
            f"- Value: {a.get('value')}, Z-score: {a.get('zscore', 'N/A'):.2f}"
            for a in anomalies[:5]
        ])
        
        prompt = f"""Analyze these anomalies detected in column '{column}':

{anomaly_text}

Column Statistics:
- Mean: {stats.get('mean', 'N/A')}
- Std Dev: {stats.get('std', 'N/A')}
- Min: {stats.get('min', 'N/A')}
- Max: {stats.get('max', 'N/A')}

Provide:
1. Assessment of whether these are true anomalies or data errors
2. Potential business implications
3. Recommended handling approach"""

        return self.generate_insight(prompt, {'column': column, 'anomalies': anomalies})
    
    def generate_pattern_insight(self, pattern_type: str, pattern_data: Dict) -> str:
        """Generate insight about a detected pattern"""
        prompt = f"""A {pattern_type} pattern was detected in the data:

Pattern Details:
{pattern_data}

Explain:
1. What this pattern means in plain language
2. Why this pattern might exist
3. How this insight can be used for decision-making"""

        return self.generate_insight(prompt, pattern_data)
    
    def generate_comparison_insight(self, groups: List[str], metrics: Dict, 
                                    comparison_type: str = 'categorical') -> str:
        """Generate insight comparing groups"""
        metrics_text = "\n".join([
            f"- {group}: {values}"
            for group, values in metrics.items()
        ])
        
        prompt = f"""Compare these groups based on the following metrics:

Groups: {', '.join(groups)}

Metrics:
{metrics_text}

Provide:
1. Which group performs best/worst and why
2. Key differences between groups
3. Actionable recommendations based on the comparison"""

        return self.generate_insight(prompt, {'groups': groups, 'metrics': metrics})
    
    def _build_data_context(self, df: pd.DataFrame, statistics: Dict = None) -> Dict:
        """Build context dictionary from dataframe"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        missing_total = df.isnull().sum().sum()
        total_cells = df.shape[0] * df.shape[1]
        
        stats_summary = ""
        if statistics:
            summary = statistics.get('summary', {})
            stats_summary = f"""
            - Total missing: {summary.get('total_missing', missing_total)}
            - Numeric columns: {len(numeric_cols)}
            - Categorical columns: {len(categorical_cols)}"""
        
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'numeric_cols': len(numeric_cols),
            'categorical_cols': len(categorical_cols),
            'missing_pct': (missing_total / total_cells * 100) if total_cells > 0 else 0,
            'duplicates': df.duplicated().sum(),
            'stats_summary': stats_summary,
            'column_names': df.columns.tolist()
        }
    
    def _rule_based_response(self, prompt: str, context: Dict = None) -> str:
        """Fallback rule-based response when LLM is not available"""
        context = context or {}
        
        # Simple pattern matching for different prompt types
        if 'executive summary' in prompt.lower():
            rows = context.get('rows', 0)
            cols = context.get('columns', 0)
            missing = context.get('missing_pct', 0)
            return f"""**Executive Summary** (Generated by rule-based analysis)

This dataset contains {rows:,} records across {cols} attributes. {'Data quality is excellent with minimal missing values.' if missing < 5 else f'There are {missing:.1f}% missing values that require attention.'}

The data structure supports both statistical analysis and machine learning applications. {'The dataset size provides good statistical power for reliable analysis.' if rows > 100 else 'Consider collecting more data for more robust statistical conclusions.'}

Recommended next steps: Review data quality issues, explore key correlations, and consider automated cleaning suggestions."""

        elif 'cleaning' in prompt.lower() or 'quality' in prompt.lower():
            return """**Data Quality Assessment** (Generated by rule-based analysis)

Priority recommendations:
1. Address missing values in columns with >10% gaps using appropriate imputation
2. Review and potentially remove duplicate records
3. Standardize categorical values for consistency

Impact: Unaddressed quality issues may lead to biased analysis results and unreliable predictions."""

        elif 'correlation' in prompt.lower():
            correlations = context.get('correlations', [])
            if correlations:
                top = correlations[0] if correlations else {}
                return f"""**Correlation Analysis** (Generated by rule-based analysis)

The strongest relationship found is between {top.get('column1', 'Column A')} and {top.get('column2', 'Column B')} with a correlation of {top.get('correlation', 0):.2f}.

Key considerations:
1. Strong correlations may indicate predictive relationships
2. Consider multicollinearity if using multiple correlated features in models
3. Correlation does not imply causation - further investigation recommended."""
            return "No significant correlations detected in the numeric columns."

        elif 'visualization' in prompt.lower():
            return """**Visualization Recommendations** (Generated by rule-based analysis)

1. **Distribution Charts**: Histograms for numeric columns to understand data spread
2. **Correlation Heatmap**: Visual overview of relationships between variables
3. **Box Plots**: Identify outliers and compare distributions across categories

These visualizations will help communicate key findings to stakeholders effectively."""

        return "Analysis completed. Please review the detailed statistics and recommendations above."


# Singleton instance for easy import
local_llm = LocalLLMService()


def get_llm_status() -> Dict[str, Any]:
    """Get status of local LLM service"""
    return {
        'available': local_llm.is_available,
        'model': local_llm.model,
        'host': local_llm.OLLAMA_HOST,
        'mode': 'local_llm' if local_llm.is_available else 'rule_based'
    }
