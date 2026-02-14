"""
Magic Analysis Service - One-Click Data Analysis Pipeline
Provides comprehensive automated analysis with plain-English insights
No external AI required - uses statistical and ML methods locally
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from scipy import stats
from sklearn.preprocessing import StandardScaler
from datetime import datetime


class MagicAnalysisService:
    """Orchestrates the complete one-click analysis pipeline"""
    
    def __init__(self, df: pd.DataFrame, project_name: str = "Your Data"):
        self.df = df
        self.original_df = df.copy()
        self.project_name = project_name
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        self.datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
    def run_full_analysis(self) -> Dict[str, Any]:
        """Execute the complete magic analysis pipeline"""
        result = {
            'executive_summary': self._generate_executive_summary(),
            'data_profile': self._profile_data(),
            'data_quality': self._assess_data_quality(),
            'cleaning_suggestions': self._generate_cleaning_suggestions(),
            'key_insights': self._discover_insights(),
            'suggested_visualizations': self._suggest_visualizations(),
            'next_steps': self._recommend_next_steps(),
            'analysis_timestamp': datetime.now().isoformat()
        }
        return result
    
    def _generate_executive_summary(self) -> Dict[str, Any]:
        """Generate plain-English executive summary"""
        rows, cols = self.df.shape
        missing_total = self.df.isnull().sum().sum()
        missing_pct = (missing_total / (rows * cols)) * 100 if rows * cols > 0 else 0
        duplicates = self.df.duplicated().sum()
        
        # Calculate quality score
        quality_score = self._calculate_quality_score()
        
        # Generate summary text
        quality_text = "excellent" if quality_score >= 80 else "good" if quality_score >= 60 else "fair" if quality_score >= 40 else "needs attention"
        
        summary_text = f"Your dataset '{self.project_name}' contains {rows:,} records with {cols} attributes. "
        
        if missing_pct == 0:
            summary_text += "Great news - there are no missing values! "
        elif missing_pct < 5:
            summary_text += f"Data completeness is {quality_text} with only {missing_pct:.1f}% missing values. "
        else:
            summary_text += f"There are {missing_pct:.1f}% missing values that should be addressed. "
        
        if duplicates > 0:
            summary_text += f"Found {duplicates:,} duplicate rows that may need removal. "
        
        if len(self.numeric_cols) > 0:
            summary_text += f"You have {len(self.numeric_cols)} numeric columns suitable for statistical analysis"
            if len(self.numeric_cols) >= 2:
                summary_text += " and correlation studies"
            summary_text += ". "
        
        if len(self.categorical_cols) > 0:
            summary_text += f"The {len(self.categorical_cols)} categorical columns can be used for segmentation and grouping. "
        
        return {
            'text': summary_text,
            'quality_score': quality_score,
            'quality_label': quality_text,
            'stats': {
                'total_rows': rows,
                'total_columns': cols,
                'numeric_columns': len(self.numeric_cols),
                'categorical_columns': len(self.categorical_cols),
                'datetime_columns': len(self.datetime_cols),
                'missing_values': int(missing_total),
                'missing_percentage': round(missing_pct, 2),
                'duplicate_rows': int(duplicates)
            }
        }
    
    def _calculate_quality_score(self) -> int:
        """Calculate data quality score 0-100"""
        score = 100
        rows, cols = self.df.shape
        
        if rows * cols == 0:
            return 0
        
        # Missing data penalty (max 30 points)
        missing_pct = (self.df.isnull().sum().sum() / (rows * cols)) * 100
        score -= min(missing_pct * 1.5, 30)
        
        # Duplicate penalty (max 20 points)
        dup_pct = (self.df.duplicated().sum() / rows) * 100 if rows > 0 else 0
        score -= min(dup_pct, 20)
        
        # Small dataset penalty
        if rows < 50:
            score -= 15
        elif rows < 100:
            score -= 8
        
        # Consistency bonus for complete columns
        complete_cols = (self.df.isnull().sum() == 0).sum()
        if complete_cols == cols:
            score += 5
        
        return max(0, min(100, round(score)))
    
    def _profile_data(self) -> Dict[str, Any]:
        """Profile each column with key statistics"""
        profile = {
            'columns': [],
            'summary': {
                'total_columns': len(self.df.columns),
                'column_types': {
                    'numeric': len(self.numeric_cols),
                    'categorical': len(self.categorical_cols),
                    'datetime': len(self.datetime_cols)
                }
            }
        }
        
        for col in self.df.columns:
            col_profile = self._profile_column(col)
            profile['columns'].append(col_profile)
        
        return profile
    
    def _profile_column(self, column: str) -> Dict[str, Any]:
        """Generate detailed profile for a single column"""
        col_data = self.df[column]
        missing = col_data.isnull().sum()
        missing_pct = (missing / len(self.df)) * 100 if len(self.df) > 0 else 0
        unique = col_data.nunique()
        
        profile = {
            'name': column,
            'dtype': str(col_data.dtype),
            'missing_count': int(missing),
            'missing_percentage': round(missing_pct, 2),
            'unique_values': int(unique),
            'uniqueness_ratio': round(unique / len(col_data) * 100, 2) if len(col_data) > 0 else 0
        }
        
        if column in self.numeric_cols:
            profile['type'] = 'numeric'
            col_clean = col_data.dropna()
            if len(col_clean) > 0:
                profile['statistics'] = {
                    'mean': round(float(col_clean.mean()), 4),
                    'median': round(float(col_clean.median()), 4),
                    'std': round(float(col_clean.std()), 4),
                    'min': round(float(col_clean.min()), 4),
                    'max': round(float(col_clean.max()), 4),
                    'range': round(float(col_clean.max() - col_clean.min()), 4),
                    'q25': round(float(col_clean.quantile(0.25)), 4),
                    'q75': round(float(col_clean.quantile(0.75)), 4),
                }
                if len(col_clean) > 2:
                    profile['statistics']['skewness'] = round(float(col_clean.skew()), 4)
                    profile['statistics']['kurtosis'] = round(float(col_clean.kurtosis()), 4)
                
                # Detect outliers using IQR
                q1 = col_clean.quantile(0.25)
                q3 = col_clean.quantile(0.75)
                iqr = q3 - q1
                outliers = col_clean[(col_clean < q1 - 1.5*iqr) | (col_clean > q3 + 1.5*iqr)]
                profile['outliers'] = {
                    'count': int(len(outliers)),
                    'percentage': round(len(outliers) / len(col_clean) * 100, 2)
                }
                
                # Distribution type
                profile['distribution_type'] = self._infer_distribution(col_clean)
                
                # Zeros and negatives
                profile['zeros'] = int((col_data == 0).sum())
                profile['negatives'] = int((col_data < 0).sum())
                
        elif column in self.categorical_cols:
            profile['type'] = 'categorical'
            value_counts = col_data.value_counts()
            profile['top_values'] = [
                {'value': str(k), 'count': int(v), 'percentage': round(v / len(col_data) * 100, 2)}
                for k, v in value_counts.head(5).items()
            ]
            profile['cardinality'] = 'high' if unique > 50 else 'medium' if unique > 10 else 'low'
            
            # Check for potential issues
            if unique == 1:
                profile['issue'] = 'single_value'
            elif unique == len(col_data):
                profile['issue'] = 'unique_identifier'
                
        elif column in self.datetime_cols:
            profile['type'] = 'datetime'
            col_clean = col_data.dropna()
            if len(col_clean) > 0:
                profile['range'] = {
                    'min': str(col_clean.min()),
                    'max': str(col_clean.max()),
                    'span_days': int((col_clean.max() - col_clean.min()).days)
                }
        else:
            profile['type'] = 'unknown'
        
        return profile
    
    def _infer_distribution(self, data: pd.Series) -> str:
        """Infer distribution type from data"""
        if len(data) < 8:
            return 'insufficient_data'
        
        skew = float(data.skew())
        kurt = float(data.kurtosis())
        
        if abs(skew) < 0.5 and abs(kurt) < 1:
            return 'normal'
        elif skew > 1:
            return 'right_skewed'
        elif skew < -1:
            return 'left_skewed'
        elif kurt > 3:
            return 'heavy_tailed'
        elif kurt < -1:
            return 'light_tailed'
        return 'unknown'
    
    def _assess_data_quality(self) -> Dict[str, Any]:
        """Assess overall data quality with detailed issues"""
        issues = []
        
        # Check for missing values by column
        missing_by_col = self.df.isnull().sum()
        for col, missing_count in missing_by_col.items():
            if missing_count > 0:
                pct = missing_count / len(self.df) * 100
                severity = 'critical' if pct > 30 else 'warning' if pct > 10 else 'info'
                issues.append({
                    'type': 'missing_values',
                    'column': col,
                    'count': int(missing_count),
                    'percentage': round(pct, 2),
                    'severity': severity,
                    'message': f"'{col}' has {missing_count:,} missing values ({pct:.1f}%)"
                })
        
        # Check for duplicates
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            pct = duplicates / len(self.df) * 100
            issues.append({
                'type': 'duplicates',
                'column': None,
                'count': int(duplicates),
                'percentage': round(pct, 2),
                'severity': 'warning' if pct > 5 else 'info',
                'message': f"Found {duplicates:,} duplicate rows ({pct:.1f}%)"
            })
        
        # Check for outliers in numeric columns
        for col in self.numeric_cols:
            col_data = self.df[col].dropna()
            if len(col_data) > 0:
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                outliers = col_data[(col_data < q1 - 1.5*iqr) | (col_data > q3 + 1.5*iqr)]
                if len(outliers) > 0:
                    pct = len(outliers) / len(col_data) * 100
                    if pct > 1:  # Only report if more than 1%
                        issues.append({
                            'type': 'outliers',
                            'column': col,
                            'count': int(len(outliers)),
                            'percentage': round(pct, 2),
                            'severity': 'info',
                            'message': f"'{col}' has {len(outliers)} potential outliers ({pct:.1f}%)"
                        })
        
        # Check for high cardinality categorical columns
        for col in self.categorical_cols:
            unique = self.df[col].nunique()
            if unique > 100:
                issues.append({
                    'type': 'high_cardinality',
                    'column': col,
                    'count': int(unique),
                    'percentage': round(unique / len(self.df) * 100, 2),
                    'severity': 'info',
                    'message': f"'{col}' has {unique} unique values - may need grouping"
                })
        
        # Check for constant columns
        for col in self.df.columns:
            if self.df[col].nunique() == 1:
                issues.append({
                    'type': 'constant_column',
                    'column': col,
                    'count': 1,
                    'percentage': 0,
                    'severity': 'warning',
                    'message': f"'{col}' has only one unique value - provides no information"
                })
        
        # Sort by severity
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        issues.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        return {
            'quality_score': self._calculate_quality_score(),
            'total_issues': len(issues),
            'critical_issues': len([i for i in issues if i['severity'] == 'critical']),
            'warning_issues': len([i for i in issues if i['severity'] == 'warning']),
            'info_issues': len([i for i in issues if i['severity'] == 'info']),
            'issues': issues
        }
    
    def _generate_cleaning_suggestions(self) -> List[Dict[str, Any]]:
        """Generate actionable cleaning suggestions with user options"""
        suggestions = []
        
        # Suggestions for missing values
        for col in self.df.columns:
            missing = self.df[col].isnull().sum()
            if missing > 0:
                missing_pct = missing / len(self.df) * 100
                
                suggestion = {
                    'column': col,
                    'issue': 'missing_values',
                    'count': int(missing),
                    'percentage': round(missing_pct, 2),
                    'priority': 'high' if missing_pct > 20 else 'medium' if missing_pct > 5 else 'low'
                }
                
                if col in self.numeric_cols:
                    col_data = self.df[col].dropna()
                    skewness = col_data.skew() if len(col_data) > 2 else 0
                    
                    # Recommend based on distribution
                    if abs(skewness) > 1:
                        recommended = 'median'
                        reason = f"Column is skewed (skew={skewness:.2f}), median is more robust"
                    else:
                        recommended = 'mean'
                        reason = "Column is approximately symmetric, mean is appropriate"
                    
                    suggestion['options'] = [
                        {
                            'strategy': 'mean',
                            'description': f'Fill with mean ({col_data.mean():.2f})',
                            'recommended': recommended == 'mean'
                        },
                        {
                            'strategy': 'median',
                            'description': f'Fill with median ({col_data.median():.2f})',
                            'recommended': recommended == 'median'
                        },
                        {
                            'strategy': 'mode',
                            'description': 'Fill with most common value',
                            'recommended': False
                        },
                        {
                            'strategy': 'forward_fill',
                            'description': 'Fill with previous value (for sequential data)',
                            'recommended': False
                        },
                        {
                            'strategy': 'constant',
                            'description': 'Fill with custom value (e.g., 0 or -1)',
                            'recommended': False
                        },
                        {
                            'strategy': 'drop_rows',
                            'description': f'Remove rows with missing values ({missing:,} rows)',
                            'recommended': missing_pct < 5
                        }
                    ]
                    suggestion['reason'] = reason
                    
                else:  # Categorical column
                    mode_val = self.df[col].mode()[0] if len(self.df[col].mode()) > 0 else 'Unknown'
                    suggestion['options'] = [
                        {
                            'strategy': 'mode',
                            'description': f"Fill with most common value ('{mode_val}')",
                            'recommended': True
                        },
                        {
                            'strategy': 'constant',
                            'description': "Fill with 'Unknown' or custom value",
                            'recommended': False
                        },
                        {
                            'strategy': 'drop_rows',
                            'description': f'Remove rows with missing values ({missing:,} rows)',
                            'recommended': missing_pct < 5
                        }
                    ]
                    suggestion['reason'] = f"For categorical data, using the mode ('{mode_val}') is recommended"
                
                suggestions.append(suggestion)
        
        # Suggestions for data type conversion
        for col in self.categorical_cols:
            col_data = self.df[col].dropna()
            if len(col_data) > 0:
                # Check if numeric
                try:
                    numeric_converted = pd.to_numeric(col_data, errors='coerce')
                    valid_pct = numeric_converted.notna().sum() / len(col_data) * 100
                    if valid_pct > 90:
                        suggestions.append({
                            'column': col,
                            'issue': 'type_conversion',
                            'count': int(len(col_data)),
                            'percentage': round(valid_pct, 2),
                            'priority': 'medium',
                            'options': [
                                {
                                    'strategy': 'to_numeric',
                                    'description': f'Convert to numeric (valid: {valid_pct:.1f}%)',
                                    'recommended': True
                                },
                                {
                                    'strategy': 'keep_as_string',
                                    'description': 'Keep as text',
                                    'recommended': False
                                }
                            ],
                            'reason': f'{valid_pct:.1f}% of values are valid numbers'
                        })
                except Exception:
                    pass
        
        # Suggestions for text normalization
        for col in self.categorical_cols:
            col_data = self.df[col].dropna().astype(str)
            if len(col_data) > 0:
                # Check for whitespace issues
                has_whitespace = col_data.str.strip() != col_data
                whitespace_count = has_whitespace.sum()
                
                if whitespace_count > 0:
                    suggestions.append({
                        'column': col,
                        'issue': 'text_normalization',
                        'count': int(whitespace_count),
                        'percentage': round(whitespace_count / len(col_data) * 100, 2),
                        'priority': 'low',
                        'options': [
                            {
                                'strategy': 'trim',
                                'description': f'Remove leading/trailing whitespace ({whitespace_count} values)',
                                'recommended': True
                            },
                            {
                                'strategy': 'lowercase',
                                'description': 'Convert to lowercase',
                                'recommended': False
                            },
                            {
                                'strategy': 'uppercase',
                                'description': 'Convert to uppercase',
                                'recommended': False
                            },
                            {
                                'strategy': 'remove_special',
                                'description': 'Remove special characters',
                                'recommended': False
                            }
                        ],
                        'reason': f'{whitespace_count} values have leading/trailing whitespace'
                    })
        
        # Suggestion for duplicates
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            suggestions.append({
                'column': '__all__',
                'issue': 'duplicates',
                'count': int(duplicates),
                'percentage': round(duplicates / len(self.df) * 100, 2),
                'priority': 'medium' if duplicates / len(self.df) > 0.05 else 'low',
                'options': [
                    {
                        'strategy': 'remove_duplicates',
                        'description': f'Remove all {duplicates:,} duplicate rows',
                        'recommended': True
                    },
                    {
                        'strategy': 'keep_first',
                        'description': 'Keep first occurrence of each duplicate',
                        'recommended': False
                    },
                    {
                        'strategy': 'keep_last',
                        'description': 'Keep last occurrence of each duplicate',
                        'recommended': False
                    }
                ],
                'reason': f'Duplicates may skew analysis results'
            })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return suggestions
    
    def _discover_insights(self) -> List[Dict[str, Any]]:
        """Discover and generate key insights from the data"""
        insights = []
        
        # Insight: Data size assessment
        rows, cols = self.df.shape
        if rows < 100:
            insights.append({
                'type': 'data_size',
                'icon': 'info',
                'title': 'Small Dataset',
                'message': f"Your dataset has {rows:,} rows. While analysis is possible, results may be more reliable with more data.",
                'priority': 'medium'
            })
        elif rows > 100000:
            insights.append({
                'type': 'data_size',
                'icon': 'success',
                'title': 'Large Dataset',
                'message': f"With {rows:,} rows, you have excellent statistical power for robust analysis.",
                'priority': 'low'
            })
        
        # Insight: Strong correlations
        if len(self.numeric_cols) >= 2:
            corr_matrix = self.df[self.numeric_cols].corr()
            for i, col1 in enumerate(self.numeric_cols):
                for col2 in self.numeric_cols[i+1:]:
                    corr = corr_matrix.loc[col1, col2]
                    if not np.isnan(corr) and abs(corr) > 0.7:
                        direction = "positive" if corr > 0 else "negative"
                        strength = "very strong" if abs(corr) > 0.9 else "strong"
                        insights.append({
                            'type': 'correlation',
                            'icon': 'link',
                            'title': f'{strength.title()} Relationship Found',
                            'message': f"'{col1}' and '{col2}' have a {strength} {direction} correlation ({corr:.2f}). When one increases, the other {'increases' if corr > 0 else 'decreases'}.",
                            'priority': 'high',
                            'columns': [col1, col2],
                            'correlation': round(float(corr), 4)
                        })
        
        # Insight: Skewed distributions
        for col in self.numeric_cols:
            col_data = self.df[col].dropna()
            if len(col_data) > 2:
                skewness = col_data.skew()
                if abs(skewness) > 1:
                    direction = "right" if skewness > 0 else "left"
                    insights.append({
                        'type': 'distribution',
                        'icon': 'chart',
                        'title': f'Skewed Distribution in {col}',
                        'message': f"'{col}' is {direction}-skewed (skew={skewness:.2f}). The average ({col_data.mean():.2f}) differs significantly from the median ({col_data.median():.2f}).",
                        'priority': 'medium',
                        'column': col
                    })
        
        # Insight: Dominant categories
        for col in self.categorical_cols:
            value_counts = self.df[col].value_counts()
            if len(value_counts) > 1:
                top_val = value_counts.iloc[0]
                top_name = value_counts.index[0]
                total = value_counts.sum()
                pct = top_val / total * 100
                if pct > 50:
                    insights.append({
                        'type': 'category_dominance',
                        'icon': 'alert',
                        'title': f'Dominant Category in {col}',
                        'message': f"'{top_name}' dominates '{col}' with {pct:.1f}% of all values. This may indicate imbalanced data.",
                        'priority': 'medium',
                        'column': col,
                        'dominant_value': str(top_name),
                        'percentage': round(pct, 2)
                    })
        
        # Insight: Date range
        for col in self.datetime_cols:
            col_data = self.df[col].dropna()
            if len(col_data) > 0:
                span = (col_data.max() - col_data.min()).days
                insights.append({
                    'type': 'date_range',
                    'icon': 'calendar',
                    'title': f'Time Range in {col}',
                    'message': f"Data spans {span} days from {col_data.min().strftime('%Y-%m-%d')} to {col_data.max().strftime('%Y-%m-%d')}.",
                    'priority': 'low',
                    'column': col
                })
        
        # Insight: ML readiness
        if len(self.numeric_cols) >= 3:
            insights.append({
                'type': 'ml_ready',
                'icon': 'brain',
                'title': 'Machine Learning Ready',
                'message': f"With {len(self.numeric_cols)} numeric columns, your data is suitable for building prediction models, clustering, or dimensionality reduction.",
                'priority': 'low'
            })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        insights.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return insights[:15]  # Return top 15 insights
    
    def _suggest_visualizations(self) -> List[Dict[str, Any]]:
        """Suggest appropriate visualizations based on data characteristics"""
        visualizations = []
        
        # Distribution charts for numeric columns
        for col in self.numeric_cols[:5]:  # Limit to first 5
            col_data = self.df[col].dropna()
            if len(col_data) > 0:
                visualizations.append({
                    'type': 'histogram',
                    'title': f'Distribution of {col}',
                    'description': f'See how values are spread across {col}',
                    'columns': [col],
                    'config': {
                        'x_column': col,
                        'bins': 20
                    }
                })
        
        # Correlation heatmap if multiple numeric columns
        if len(self.numeric_cols) >= 2:
            visualizations.append({
                'type': 'heatmap',
                'title': 'Correlation Heatmap',
                'description': f'Relationships between all {len(self.numeric_cols)} numeric variables',
                'columns': self.numeric_cols,
                'config': {}
            })
        
        # Scatter plots for correlated pairs
        if len(self.numeric_cols) >= 2:
            corr_matrix = self.df[self.numeric_cols].corr()
            for i, col1 in enumerate(self.numeric_cols[:5]):
                for col2 in self.numeric_cols[i+1:5]:
                    corr = corr_matrix.loc[col1, col2]
                    if not np.isnan(corr) and abs(corr) > 0.5:
                        visualizations.append({
                            'type': 'scatter',
                            'title': f'{col1} vs {col2}',
                            'description': f'Explore the relationship (r={corr:.2f})',
                            'columns': [col1, col2],
                            'config': {
                                'x_column': col1,
                                'y_column': col2
                            }
                        })
        
        # Bar charts for categorical columns
        for col in self.categorical_cols[:3]:  # Limit to first 3
            unique = self.df[col].nunique()
            if 2 <= unique <= 20:  # Only if reasonable number of categories
                visualizations.append({
                    'type': 'bar',
                    'title': f'{col} Distribution',
                    'description': f'Count of each {col} category',
                    'columns': [col],
                    'config': {
                        'x_column': col
                    }
                })
        
        # Pie chart for binary/few category columns
        for col in self.categorical_cols:
            unique = self.df[col].nunique()
            if 2 <= unique <= 6:
                visualizations.append({
                    'type': 'pie',
                    'title': f'{col} Breakdown',
                    'description': f'Proportion of each {col} category',
                    'columns': [col],
                    'config': {
                        'column': col
                    }
                })
                break  # Only one pie chart
        
        # Box plots for outlier visualization
        outlier_cols = []
        for col in self.numeric_cols:
            col_data = self.df[col].dropna()
            if len(col_data) > 0:
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                outliers = col_data[(col_data < q1 - 1.5*iqr) | (col_data > q3 + 1.5*iqr)]
                if len(outliers) > 0:
                    outlier_cols.append(col)
        
        if outlier_cols:
            visualizations.append({
                'type': 'box',
                'title': 'Outlier Detection',
                'description': f'Box plots showing outliers in {len(outlier_cols)} columns',
                'columns': outlier_cols[:5],
                'config': {}
            })
        
        return visualizations[:10]  # Return top 10 suggestions
    
    def _recommend_next_steps(self) -> List[Dict[str, Any]]:
        """Recommend next steps based on analysis"""
        steps = []
        
        # Step 1: Address critical issues
        missing_cols = [col for col in self.df.columns if self.df[col].isnull().sum() > 0]
        if missing_cols:
            steps.append({
                'step': 1,
                'action': 'Handle Missing Values',
                'description': f'Address missing values in {len(missing_cols)} columns to improve data quality',
                'type': 'cleaning',
                'affected_columns': missing_cols
            })
        
        # Step 2: Remove duplicates
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            steps.append({
                'step': 2,
                'action': 'Remove Duplicates',
                'description': f'Remove {duplicates:,} duplicate rows to prevent skewed analysis',
                'type': 'cleaning',
                'affected_columns': ['__all__']
            })
        
        # Step 3: Explore correlations
        if len(self.numeric_cols) >= 2:
            steps.append({
                'step': 3,
                'action': 'Explore Relationships',
                'description': 'Examine correlation matrix to understand how variables relate',
                'type': 'analysis',
                'affected_columns': self.numeric_cols
            })
        
        # Step 4: Try ML models
        if len(self.numeric_cols) >= 2:
            steps.append({
                'step': 4,
                'action': 'Build Prediction Models',
                'description': 'Use machine learning to predict outcomes or discover patterns',
                'type': 'ml',
                'affected_columns': self.numeric_cols
            })
        
        # Step 5: Export results
        steps.append({
            'step': 5,
            'action': 'Export Clean Data',
            'description': 'Export your cleaned and transformed data for further use',
            'type': 'export',
            'affected_columns': list(self.df.columns)
        })
        
        return steps


def run_magic_analysis(df: pd.DataFrame, project_name: str = "Your Data") -> Dict[str, Any]:
    """Main entry point for magic analysis"""
    service = MagicAnalysisService(df, project_name)
    return service.run_full_analysis()
