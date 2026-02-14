"""
Rule-Based Insights Generator for AnalytiCore
Generates intelligent insights and recommendations using algorithmic logic
NO AI/LLM required - works completely offline and FREE
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional


class RuleBasedInsightsGenerator:
    """Generates data insights using rule-based algorithmic logic"""
    
    def __init__(self, statistics: dict, correlation: dict = None):
        self.stats = statistics
        self.correlation = correlation
        self.summary = statistics.get('summary', {})
        self.numeric_stats = statistics.get('numeric', {})
        self.categorical_stats = statistics.get('categorical', {})
        self.datetime_stats = statistics.get('datetime', {})
    
    def generate_quick_insights(self) -> dict:
        """Generate comprehensive insights from statistics"""
        
        insights = {
            'executive_summary': self._generate_executive_summary(),
            'key_findings': self._generate_key_findings(),
            'data_quality_issues': self._generate_quality_issues(),
            'patterns_discovered': self._generate_patterns(),
            'recommendations': self._generate_recommendations()
        }
        
        return insights
    
    def _generate_executive_summary(self) -> str:
        """Generate a concise executive summary"""
        total_rows = self.summary.get('total_rows', 0)
        total_cols = self.summary.get('total_columns', 0)
        numeric_cols = self.summary.get('numeric_columns', 0)
        categorical_cols = self.summary.get('categorical_columns', 0)
        total_missing = self.summary.get('total_missing', 0)
        duplicates = self.summary.get('total_duplicates', 0)
        
        # Calculate overall data quality score
        total_cells = total_rows * total_cols if total_rows and total_cols else 1
        missing_pct = (total_missing / total_cells) * 100 if total_cells > 0 else 0
        
        quality = "excellent" if missing_pct < 1 else "good" if missing_pct < 5 else "moderate" if missing_pct < 15 else "poor"
        
        summary_parts = [
            f"This dataset contains {total_rows:,} rows and {total_cols} columns ({numeric_cols} numeric, {categorical_cols} categorical)."
        ]
        
        if missing_pct > 0:
            summary_parts.append(f"Data quality is {quality} with {missing_pct:.1f}% missing values ({total_missing:,} cells).")
        else:
            summary_parts.append("Data quality is excellent with no missing values.")
        
        if duplicates > 0:
            dup_pct = (duplicates / total_rows) * 100 if total_rows > 0 else 0
            summary_parts.append(f"Found {duplicates:,} duplicate rows ({dup_pct:.1f}%).")
        
        # Add correlation insight if available
        if self.correlation and self.correlation.get('top_correlations'):
            top_corr = self.correlation['top_correlations'][0]
            if abs(top_corr['correlation']) >= 0.7:
                summary_parts.append(
                    f"Strong correlation detected between {top_corr['column1']} and {top_corr['column2']} ({top_corr['correlation']:.2f})."
                )
        
        return " ".join(summary_parts)
    
    def _generate_key_findings(self) -> List[dict]:
        """Generate key findings from the data"""
        findings = []
        
        # Finding: Dataset size
        total_rows = self.summary.get('total_rows', 0)
        if total_rows > 100000:
            findings.append({
                'finding': f"Large dataset with {total_rows:,} rows - consider sampling for initial exploration",
                'importance': 'medium'
            })
        elif total_rows < 100:
            findings.append({
                'finding': f"Small dataset with only {total_rows} rows - statistical conclusions may be limited",
                'importance': 'high'
            })
        
        # Finding: Numeric column insights
        for col, stats in self.numeric_stats.items():
            # High variance
            if stats.get('std') and stats.get('mean'):
                cv = abs(stats['std'] / stats['mean']) if stats['mean'] != 0 else 0
                if cv > 1:
                    findings.append({
                        'finding': f"Column '{col}' has high variability (CV={cv:.2f}) - values are widely spread",
                        'importance': 'medium'
                    })
            
            # Skewness
            skewness = stats.get('skewness')
            if skewness and abs(skewness) > 2:
                direction = "right" if skewness > 0 else "left"
                findings.append({
                    'finding': f"Column '{col}' is heavily {direction}-skewed (skew={skewness:.2f}) - consider log transformation",
                    'importance': 'medium'
                })
            
            # All same values
            if stats.get('std') == 0:
                findings.append({
                    'finding': f"Column '{col}' has no variation - all values are identical ({stats.get('mean')})",
                    'importance': 'high'
                })
        
        # Finding: Categorical insights
        for col, stats in self.categorical_stats.items():
            unique = stats.get('unique', 0)
            count = stats.get('count', 1)
            
            # High cardinality
            if unique > 100:
                findings.append({
                    'finding': f"Column '{col}' has high cardinality ({unique} unique values) - may need grouping or encoding",
                    'importance': 'medium'
                })
            
            # Dominant category
            if stats.get('freq') and count > 0:
                freq_pct = (stats['freq'] / count) * 100
                if freq_pct > 80:
                    findings.append({
                        'finding': f"Column '{col}' is dominated by '{stats.get('top')}' ({freq_pct:.1f}%) - imbalanced distribution",
                        'importance': 'medium'
                    })
        
        # Finding: Correlations
        if self.correlation and self.correlation.get('top_correlations'):
            strong_corrs = [c for c in self.correlation['top_correlations'] if abs(c['correlation']) >= 0.8]
            if strong_corrs:
                findings.append({
                    'finding': f"Found {len(strong_corrs)} strongly correlated column pair(s) - potential multicollinearity",
                    'importance': 'high'
                })
        
        # Sort by importance
        importance_order = {'high': 0, 'medium': 1, 'low': 2}
        findings.sort(key=lambda x: importance_order.get(x['importance'], 2))
        
        return findings[:10]  # Return top 10 findings
    
    def _generate_quality_issues(self) -> List[dict]:
        """Identify data quality issues"""
        issues = []
        
        # Issue: Missing values
        for col, stats in self.numeric_stats.items():
            missing_pct = stats.get('missing_pct', 0)
            if missing_pct > 0:
                severity = 'critical' if missing_pct > 20 else 'warning' if missing_pct > 5 else 'info'
                issues.append({
                    'issue': f"Column '{col}' has {stats.get('missing', 0)} missing values ({missing_pct:.1f}%)",
                    'severity': severity,
                    'affected_columns': [col]
                })
        
        for col, stats in self.categorical_stats.items():
            missing_pct = stats.get('missing_pct', 0)
            if missing_pct > 0:
                severity = 'critical' if missing_pct > 20 else 'warning' if missing_pct > 5 else 'info'
                issues.append({
                    'issue': f"Column '{col}' has {stats.get('missing', 0)} missing values ({missing_pct:.1f}%)",
                    'severity': severity,
                    'affected_columns': [col]
                })
        
        # Issue: Duplicates
        duplicates = self.summary.get('total_duplicates', 0)
        if duplicates > 0:
            total_rows = self.summary.get('total_rows', 1)
            dup_pct = (duplicates / total_rows) * 100
            severity = 'critical' if dup_pct > 10 else 'warning' if dup_pct > 1 else 'info'
            issues.append({
                'issue': f"Dataset contains {duplicates:,} duplicate rows ({dup_pct:.1f}%)",
                'severity': severity,
                'affected_columns': ['all']
            })
        
        # Issue: Potential outliers
        for col, stats in self.numeric_stats.items():
            if stats.get('iqr') and stats.get('25%') and stats.get('75%'):
                q1, q3, iqr = stats['25%'], stats['75%'], stats['iqr']
                min_val, max_val = stats.get('min', 0), stats.get('max', 0)
                
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                if min_val < lower_bound or max_val > upper_bound:
                    issues.append({
                        'issue': f"Column '{col}' may contain outliers (values outside [{lower_bound:.2f}, {upper_bound:.2f}])",
                        'severity': 'warning',
                        'affected_columns': [col]
                    })
        
        # Issue: Zero variance
        for col, stats in self.numeric_stats.items():
            if stats.get('std') == 0:
                issues.append({
                    'issue': f"Column '{col}' has zero variance - provides no information",
                    'severity': 'warning',
                    'affected_columns': [col]
                })
        
        # Sort by severity
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        issues.sort(key=lambda x: severity_order.get(x['severity'], 2))
        
        return issues
    
    def _generate_patterns(self) -> List[dict]:
        """Discover patterns in the data"""
        patterns = []
        
        # Pattern: Strong correlations
        if self.correlation and self.correlation.get('top_correlations'):
            for corr in self.correlation['top_correlations'][:5]:
                if abs(corr['correlation']) >= 0.6:
                    direction = "positive" if corr['correlation'] > 0 else "negative"
                    patterns.append({
                        'pattern': f"Strong {direction} correlation ({corr['correlation']:.2f}) between '{corr['column1']}' and '{corr['column2']}'",
                        'columns_involved': [corr['column1'], corr['column2']]
                    })
        
        # Pattern: Similar distributions
        numeric_cols = list(self.numeric_stats.keys())
        for i, col1 in enumerate(numeric_cols):
            for col2 in numeric_cols[i+1:]:
                stats1, stats2 = self.numeric_stats[col1], self.numeric_stats[col2]
                
                # Check if distributions are similar (similar skewness and kurtosis)
                if stats1.get('skewness') and stats2.get('skewness'):
                    if abs(stats1['skewness'] - stats2['skewness']) < 0.5:
                        if stats1.get('kurtosis') and stats2.get('kurtosis'):
                            if abs(stats1['kurtosis'] - stats2['kurtosis']) < 1:
                                patterns.append({
                                    'pattern': f"Columns '{col1}' and '{col2}' have similar distributions",
                                    'columns_involved': [col1, col2]
                                })
        
        # Pattern: Categorical dominance
        for col, stats in self.categorical_stats.items():
            value_counts = stats.get('value_counts', {})
            if len(value_counts) >= 2:
                sorted_counts = sorted(value_counts.values(), reverse=True)
                if len(sorted_counts) >= 2 and sorted_counts[0] > sorted_counts[1] * 3:
                    patterns.append({
                        'pattern': f"Column '{col}' has a dominant category that appears 3x more than others",
                        'columns_involved': [col]
                    })
        
        return patterns[:8]  # Return top 8 patterns
    
    def _generate_recommendations(self) -> List[dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Recommendation: Handle missing values
        cols_with_missing = []
        for col, stats in {**self.numeric_stats, **self.categorical_stats}.items():
            if stats.get('missing_pct', 0) > 0:
                cols_with_missing.append((col, stats.get('missing_pct', 0)))
        
        if cols_with_missing:
            high_missing = [c for c, pct in cols_with_missing if pct > 20]
            low_missing = [c for c, pct in cols_with_missing if pct <= 20]
            
            if high_missing:
                recommendations.append({
                    'action': f"Consider dropping columns with >20% missing: {', '.join(high_missing[:3])}",
                    'priority': 'high',
                    'reason': 'High missing percentage makes imputation unreliable'
                })
            
            if low_missing:
                recommendations.append({
                    'action': f"Impute missing values in: {', '.join(low_missing[:3])}",
                    'priority': 'medium',
                    'reason': 'Use mean/median for numeric, mode for categorical columns'
                })
        
        # Recommendation: Handle duplicates
        if self.summary.get('total_duplicates', 0) > 0:
            recommendations.append({
                'action': 'Remove duplicate rows from the dataset',
                'priority': 'high',
                'reason': f"Found {self.summary['total_duplicates']:,} duplicate rows that may skew analysis"
            })
        
        # Recommendation: Handle outliers
        for col, stats in self.numeric_stats.items():
            if stats.get('iqr') and stats.get('skewness'):
                if abs(stats['skewness']) > 2:
                    recommendations.append({
                        'action': f"Apply log transformation to '{col}' to reduce skewness",
                        'priority': 'medium',
                        'reason': f"Column is heavily skewed (skewness={stats['skewness']:.2f})"
                    })
                    break  # Only one outlier recommendation
        
        # Recommendation: Handle high cardinality
        for col, stats in self.categorical_stats.items():
            if stats.get('unique', 0) > 50:
                recommendations.append({
                    'action': f"Consider grouping or encoding high-cardinality column '{col}'",
                    'priority': 'medium',
                    'reason': f"Column has {stats['unique']} unique values - may cause issues in modeling"
                })
                break
        
        # Recommendation: Feature engineering from correlations
        if self.correlation and self.correlation.get('top_correlations'):
            strong_corrs = [c for c in self.correlation['top_correlations'] if abs(c['correlation']) >= 0.9]
            if strong_corrs:
                corr = strong_corrs[0]
                recommendations.append({
                    'action': f"Consider removing one of '{corr['column1']}' or '{corr['column2']}' (correlation={corr['correlation']:.2f})",
                    'priority': 'medium',
                    'reason': 'Highly correlated features provide redundant information'
                })
        
        # Recommendation: Data validation
        total_rows = self.summary.get('total_rows', 0)
        if total_rows < 100:
            recommendations.append({
                'action': 'Collect more data if possible - current sample is small',
                'priority': 'high',
                'reason': f'Only {total_rows} rows may not be sufficient for reliable analysis'
            })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 2))
        
        return recommendations[:8]  # Return top 8 recommendations


class RuleBasedCleaningRecommender:
    """Generates cleaning recommendations using rule-based logic"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    def generate_recommendations(self) -> List[dict]:
        """Generate cleaning recommendations for all columns"""
        recommendations = []
        
        for col in self.df.columns:
            col_recommendations = self._analyze_column(col)
            recommendations.extend(col_recommendations)
        
        # Add global recommendations
        recommendations.extend(self._global_recommendations())
        
        return recommendations
    
    def _analyze_column(self, column: str) -> List[dict]:
        """Analyze a single column and generate recommendations"""
        recs = []
        col_data = self.df[column]
        
        # Check for missing values
        missing_count = col_data.isnull().sum()
        missing_pct = (missing_count / len(self.df)) * 100
        
        if missing_count > 0:
            if column in self.numeric_cols:
                # Determine best fill strategy
                skewness = col_data.skew() if len(col_data.dropna()) > 2 else 0
                
                if abs(skewness) > 1:
                    strategy = 'median'
                    reason = f"Column is skewed (skewness={skewness:.2f}), median is more robust"
                else:
                    strategy = 'mean'
                    reason = f"Column is approximately symmetric, mean is appropriate"
                
                recs.append({
                    'column': column,
                    'issue': f'{missing_count} missing values ({missing_pct:.1f}%)',
                    'recommendation': f'Fill missing values with {strategy}',
                    'action_type': 'fill_missing',
                    'parameters': {'strategy': strategy}
                })
            else:
                # Categorical column
                mode_val = col_data.mode()[0] if len(col_data.mode()) > 0 else 'Unknown'
                recs.append({
                    'column': column,
                    'issue': f'{missing_count} missing values ({missing_pct:.1f}%)',
                    'recommendation': f"Fill missing values with mode ('{mode_val}')",
                    'action_type': 'fill_missing',
                    'parameters': {'strategy': 'mode'}
                })
        
        # Check for outliers (numeric only)
        if column in self.numeric_cols:
            col_clean = col_data.dropna()
            if len(col_clean) > 0:
                Q1 = col_clean.quantile(0.25)
                Q3 = col_clean.quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                
                outliers = col_clean[(col_clean < lower) | (col_clean > upper)]
                if len(outliers) > 0:
                    outlier_pct = (len(outliers) / len(col_clean)) * 100
                    if outlier_pct > 1:  # More than 1% outliers
                        recs.append({
                            'column': column,
                            'issue': f'{len(outliers)} potential outliers ({outlier_pct:.1f}%)',
                            'recommendation': 'Cap or remove outliers using IQR method',
                            'action_type': 'remove_outliers',
                            'parameters': {'method': 'iqr'}
                        })
        
        # Check for potential type conversion
        if column in self.categorical_cols:
            # Check if it might be numeric
            try:
                numeric_converted = pd.to_numeric(col_data.dropna(), errors='coerce')
                valid_pct = numeric_converted.notna().sum() / len(col_data.dropna()) * 100
                if valid_pct > 90:
                    recs.append({
                        'column': column,
                        'issue': 'Column appears to contain numeric values stored as text',
                        'recommendation': 'Convert to numeric type',
                        'action_type': 'convert_type',
                        'parameters': {'target_type': 'numeric'}
                    })
            except:
                pass
            
            # Check if it might be a date
            if col_data.dtype == 'object':
                sample = col_data.dropna().head(100)
                date_patterns = ['date', 'time', 'year', 'month', 'day']
                if any(p in column.lower() for p in date_patterns):
                    try:
                        pd.to_datetime(sample, errors='raise')
                        recs.append({
                            'column': column,
                            'issue': 'Column appears to contain date/time values',
                            'recommendation': 'Convert to datetime type',
                            'action_type': 'convert_type',
                            'parameters': {'target_type': 'datetime'}
                        })
                    except:
                        pass
        
        # Check column naming
        if ' ' in column or not column[0].isalpha():
            clean_name = column.strip().replace(' ', '_').lower()
            if not clean_name[0].isalpha():
                clean_name = 'col_' + clean_name
            recs.append({
                'column': column,
                'issue': 'Column name contains spaces or starts with non-letter',
                'recommendation': f"Rename to '{clean_name}'",
                'action_type': 'rename_column',
                'parameters': {'new_name': clean_name}
            })
        
        return recs
    
    def _global_recommendations(self) -> List[dict]:
        """Generate dataset-wide recommendations"""
        recs = []
        
        # Check for duplicates
        duplicate_count = self.df.duplicated().sum()
        if duplicate_count > 0:
            recs.append({
                'column': '__all__',
                'issue': f'{duplicate_count} duplicate rows found',
                'recommendation': 'Remove duplicate rows',
                'action_type': 'remove_duplicates',
                'parameters': {}
            })
        
        return recs


def generate_insights_without_ai(statistics: dict, correlation: dict = None) -> dict:
    """Main function to generate insights without AI"""
    generator = RuleBasedInsightsGenerator(statistics, correlation)
    return generator.generate_quick_insights()


def generate_cleaning_recommendations_without_ai(df: pd.DataFrame) -> List[dict]:
    """Main function to generate cleaning recommendations without AI"""
    recommender = RuleBasedCleaningRecommender(df)
    return recommender.generate_recommendations()
