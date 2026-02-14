"""
Plain English Insights Generator
Converts statistics and data patterns into human-readable insights
"""
import pandas as pd
import numpy as np
from datetime import datetime


class PlainEnglishInsights:
    """Generate human-readable insights from data analysis"""
    
    def __init__(self, df, project_name="your data"):
        self.df = df
        self.project_name = project_name
        self.insights = []
        self.warnings = []
        self.opportunities = []
        self.summary = {}
        
    def generate_all_insights(self):
        """Generate all insights from the data"""
        self._analyze_overview()
        self._analyze_data_quality()
        self._analyze_numeric_columns()
        self._analyze_categorical_columns()
        self._analyze_correlations()
        self._analyze_trends()
        self._generate_recommendations()
        
        return {
            'summary': self.summary,
            'key_insights': self.insights[:10],  # Top 10 insights
            'warnings': self.warnings,
            'opportunities': self.opportunities,
            'data_quality_score': self._calculate_quality_score(),
            'executive_summary': self._generate_executive_summary()
        }
    
    def _analyze_overview(self):
        """Basic data overview"""
        rows, cols = self.df.shape
        
        self.summary = {
            'total_rows': rows,
            'total_columns': cols,
            'numeric_columns': len(self.df.select_dtypes(include=[np.number]).columns),
            'text_columns': len(self.df.select_dtypes(include=['object']).columns),
            'date_columns': len(self.df.select_dtypes(include=['datetime64']).columns),
        }
        
        # Size insight
        if rows < 100:
            self.insights.append({
                'type': 'info',
                'icon': '📊',
                'title': 'Small Dataset',
                'message': f"You have {rows:,} rows of data. This is a small dataset - results may vary with more data.",
                'priority': 'low'
            })
        elif rows > 100000:
            self.insights.append({
                'type': 'success',
                'icon': '📈',
                'title': 'Large Dataset',
                'message': f"Impressive! You have {rows:,} rows of data. This gives us strong statistical confidence.",
                'priority': 'medium'
            })
        else:
            self.insights.append({
                'type': 'info',
                'icon': '📊',
                'title': 'Dataset Overview',
                'message': f"Your data has {rows:,} rows and {cols} columns - a good size for analysis.",
                'priority': 'low'
            })
    
    def _analyze_data_quality(self):
        """Analyze data quality issues"""
        # Missing values
        missing = self.df.isnull().sum()
        total_missing = missing.sum()
        missing_pct = (total_missing / (self.df.shape[0] * self.df.shape[1])) * 100
        
        if total_missing > 0:
            worst_cols = missing[missing > 0].sort_values(ascending=False).head(3)
            cols_list = ', '.join([f"{col} ({(v/len(self.df)*100):.1f}%)" for col, v in worst_cols.items()])
            
            if missing_pct > 20:
                self.warnings.append({
                    'type': 'warning',
                    'icon': '⚠️',
                    'title': 'Significant Missing Data',
                    'message': f"{missing_pct:.1f}% of your data is missing. Columns most affected: {cols_list}. Consider filling or removing these.",
                    'priority': 'high',
                    'action': 'fill_missing'
                })
            elif missing_pct > 5:
                self.warnings.append({
                    'type': 'warning',
                    'icon': '⚠️',
                    'title': 'Some Missing Data',
                    'message': f"About {missing_pct:.1f}% of values are missing, mainly in: {cols_list}.",
                    'priority': 'medium',
                    'action': 'fill_missing'
                })
        else:
            self.insights.append({
                'type': 'success',
                'icon': '✅',
                'title': 'Complete Data',
                'message': "Great news! Your data has no missing values.",
                'priority': 'low'
            })
        
        # Duplicates
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            dup_pct = (duplicates / len(self.df)) * 100
            self.warnings.append({
                'type': 'warning',
                'icon': '🔄',
                'title': 'Duplicate Rows Found',
                'message': f"Found {duplicates:,} duplicate rows ({dup_pct:.1f}%). You may want to remove these.",
                'priority': 'medium',
                'action': 'remove_duplicates'
            })
    
    def _analyze_numeric_columns(self):
        """Analyze numeric columns for insights"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            data = self.df[col].dropna()
            if len(data) == 0:
                continue
                
            mean_val = data.mean()
            median_val = data.median()
            std_val = data.std()
            min_val = data.min()
            max_val = data.max()
            
            # Detect skewness in plain English
            skewness = data.skew()
            if abs(skewness) > 1:
                direction = "higher" if skewness > 0 else "lower"
                self.insights.append({
                    'type': 'info',
                    'icon': '📊',
                    'title': f'Skewed Distribution in "{col}"',
                    'message': f"Most {col} values are on the {direction} end. The average ({mean_val:,.2f}) is different from the typical value ({median_val:,.2f}).",
                    'priority': 'medium'
                })
            
            # Detect outliers
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((data < Q1 - 1.5*IQR) | (data > Q3 + 1.5*IQR)).sum()
            
            if outliers > 0:
                outlier_pct = (outliers / len(data)) * 100
                if outlier_pct > 5:
                    self.warnings.append({
                        'type': 'warning',
                        'icon': '🎯',
                        'title': f'Outliers in "{col}"',
                        'message': f"Found {outliers:,} unusual values ({outlier_pct:.1f}%) in {col}. These might be errors or special cases worth investigating.",
                        'priority': 'medium',
                        'action': 'review_outliers'
                    })
            
            # Range insight
            if max_val > 0 and min_val >= 0:
                range_ratio = max_val / max(min_val, 0.001)
                if range_ratio > 100:
                    self.insights.append({
                        'type': 'info',
                        'icon': '📏',
                        'title': f'Wide Range in "{col}"',
                        'message': f"{col} ranges from {min_val:,.2f} to {max_val:,.2f} - that's a {range_ratio:.0f}x difference!",
                        'priority': 'low'
                    })
    
    def _analyze_categorical_columns(self):
        """Analyze categorical columns"""
        cat_cols = self.df.select_dtypes(include=['object', 'category']).columns
        
        for col in cat_cols:
            data = self.df[col].dropna()
            if len(data) == 0:
                continue
            
            unique_count = data.nunique()
            total_count = len(data)
            
            # High cardinality warning
            if unique_count > 100 and unique_count / total_count > 0.5:
                self.warnings.append({
                    'type': 'warning',
                    'icon': '🏷️',
                    'title': f'Too Many Categories in "{col}"',
                    'message': f"{col} has {unique_count:,} unique values. This might be an ID column or needs grouping.",
                    'priority': 'low'
                })
            
            # Top category dominance
            top_value = data.value_counts().iloc[0]
            top_name = data.value_counts().index[0]
            top_pct = (top_value / total_count) * 100
            
            if top_pct > 50 and unique_count > 1:
                self.insights.append({
                    'type': 'info',
                    'icon': '👑',
                    'title': f'Dominant Category in "{col}"',
                    'message': f'"{top_name}" dominates {col} with {top_pct:.1f}% of all values.',
                    'priority': 'medium'
                })
    
    def _analyze_correlations(self):
        """Find and explain correlations"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return
        
        corr_matrix = self.df[numeric_cols].corr()
        
        # Find strong correlations
        strong_correlations = []
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j:  # Upper triangle only
                    corr = corr_matrix.loc[col1, col2]
                    if not np.isnan(corr) and abs(corr) > 0.7:
                        strong_correlations.append((col1, col2, corr))
        
        # Report top correlations
        strong_correlations.sort(key=lambda x: abs(x[2]), reverse=True)
        
        for col1, col2, corr in strong_correlations[:3]:
            direction = "increases" if corr > 0 else "decreases"
            strength = "strongly" if abs(corr) > 0.85 else "moderately"
            
            self.insights.append({
                'type': 'success',
                'icon': '🔗',
                'title': f'Strong Relationship Found',
                'message': f"When {col1} goes up, {col2} {strength} {direction}. (Correlation: {corr:.0%})",
                'priority': 'high'
            })
            
            self.opportunities.append({
                'type': 'opportunity',
                'icon': '💡',
                'title': f'Prediction Opportunity',
                'message': f"You could predict {col2} based on {col1} with good accuracy.",
                'priority': 'high',
                'action': 'train_model',
                'params': {'target': col2, 'feature': col1}
            })
    
    def _analyze_trends(self):
        """Detect trends in time series data"""
        # Try to find date columns
        date_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Also check object columns that might be dates
        for col in self.df.select_dtypes(include=['object']).columns:
            try:
                pd.to_datetime(self.df[col].head(100))
                date_cols.append(col)
            except:
                pass
        
        if not date_cols:
            return
        
        date_col = date_cols[0]
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for num_col in numeric_cols[:3]:  # Analyze top 3 numeric columns
            try:
                temp_df = self.df[[date_col, num_col]].dropna()
                temp_df[date_col] = pd.to_datetime(temp_df[date_col])
                temp_df = temp_df.sort_values(date_col)
                
                if len(temp_df) < 10:
                    continue
                
                # Simple trend detection
                first_half = temp_df[num_col].iloc[:len(temp_df)//2].mean()
                second_half = temp_df[num_col].iloc[len(temp_df)//2:].mean()
                
                if first_half > 0:
                    change_pct = ((second_half - first_half) / first_half) * 100
                    
                    if abs(change_pct) > 10:
                        direction = "increased" if change_pct > 0 else "decreased"
                        emoji = "📈" if change_pct > 0 else "📉"
                        
                        self.insights.append({
                            'type': 'success' if change_pct > 0 else 'warning',
                            'icon': emoji,
                            'title': f'{num_col} Trend Detected',
                            'message': f"{num_col} has {direction} by {abs(change_pct):.1f}% over the time period.",
                            'priority': 'high'
                        })
            except Exception:
                pass
    
    def _generate_recommendations(self):
        """Generate actionable recommendations"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        # If we have enough numeric columns, suggest ML
        if len(numeric_cols) >= 3:
            self.opportunities.append({
                'type': 'opportunity',
                'icon': '🤖',
                'title': 'Machine Learning Ready',
                'message': f"Your data has {len(numeric_cols)} numeric columns - perfect for building prediction models!",
                'priority': 'medium',
                'action': 'auto_ml'
            })
        
        # If we have categories, suggest segmentation
        cat_cols = self.df.select_dtypes(include=['object', 'category']).columns
        if len(cat_cols) > 0 and len(numeric_cols) > 0:
            self.opportunities.append({
                'type': 'opportunity',
                'icon': '👥',
                'title': 'Segmentation Possible',
                'message': f"You can analyze {numeric_cols[0]} by different {cat_cols[0]} categories to find patterns.",
                'priority': 'medium',
                'action': 'segment_analysis'
            })
    
    def _calculate_quality_score(self):
        """Calculate overall data quality score (0-100)"""
        score = 100
        
        # Missing data penalty
        missing_pct = (self.df.isnull().sum().sum() / (self.df.shape[0] * self.df.shape[1])) * 100
        score -= min(missing_pct * 2, 30)
        
        # Duplicate penalty
        dup_pct = (self.df.duplicated().sum() / len(self.df)) * 100
        score -= min(dup_pct, 20)
        
        # Too few rows penalty
        if len(self.df) < 50:
            score -= 20
        elif len(self.df) < 100:
            score -= 10
        
        return max(0, min(100, round(score)))
    
    def _generate_executive_summary(self):
        """Generate a plain English executive summary"""
        rows, cols = self.df.shape
        quality_score = self._calculate_quality_score()
        
        # Quality assessment
        if quality_score >= 80:
            quality_text = "excellent"
        elif quality_score >= 60:
            quality_text = "good"
        elif quality_score >= 40:
            quality_text = "fair"
        else:
            quality_text = "needs improvement"
        
        # Count insights by type
        high_priority = len([i for i in self.insights if i.get('priority') == 'high'])
        warning_count = len(self.warnings)
        opportunity_count = len(self.opportunities)
        
        summary_parts = [
            f"## 📊 Executive Summary for {self.project_name}\n",
            f"**Dataset Size:** {rows:,} rows × {cols} columns\n",
            f"**Data Quality:** {quality_score}/100 ({quality_text})\n",
            f"\n### Key Findings\n",
        ]
        
        # Add top insights
        for insight in self.insights[:3]:
            if insight.get('priority') in ['high', 'medium']:
                summary_parts.append(f"- {insight['icon']} {insight['message']}\n")
        
        # Add warnings if any
        if self.warnings:
            summary_parts.append(f"\n### ⚠️ Attention Needed ({warning_count})\n")
            for warning in self.warnings[:3]:
                summary_parts.append(f"- {warning['message']}\n")
        
        # Add opportunities
        if self.opportunities:
            summary_parts.append(f"\n### 💡 Opportunities ({opportunity_count})\n")
            for opp in self.opportunities[:3]:
                summary_parts.append(f"- {opp['message']}\n")
        
        return ''.join(summary_parts)


def generate_plain_english_insights(df, project_name="Your Data"):
    """Main function to generate insights"""
    generator = PlainEnglishInsights(df, project_name)
    return generator.generate_all_insights()
