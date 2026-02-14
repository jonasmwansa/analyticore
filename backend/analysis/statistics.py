"""
Statistical Analysis Service for AnalytiCore
Provides comprehensive statistical analysis including:
- Descriptive statistics (count, mean, std, min, 25%, median, 75%, max)
- Correlation analysis
- Distribution analysis
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Any, Optional


class StatisticalAnalyzer:
    """Performs statistical analysis on pandas DataFrames"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        self.datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    def get_descriptive_statistics(self) -> Dict[str, Any]:
        """
        Generate descriptive statistics for all columns
        Returns count, mean, std, min, 25%, 50%, 75%, max for numeric columns
        """
        result = {
            'numeric': {},
            'categorical': {},
            'datetime': {},
            'summary': {
                'total_rows': len(self.df),
                'total_columns': len(self.df.columns),
                'numeric_columns': len(self.numeric_cols),
                'categorical_columns': len(self.categorical_cols),
                'datetime_columns': len(self.datetime_cols),
                'total_missing': int(self.df.isnull().sum().sum()),
                'total_duplicates': int(self.df.duplicated().sum())
            }
        }
        
        # Numeric column statistics
        if self.numeric_cols:
            desc = self.df[self.numeric_cols].describe()
            for col in self.numeric_cols:
                col_data = self.df[col].dropna()
                result['numeric'][col] = {
                    'count': int(desc.loc['count', col]) if col in desc.columns else 0,
                    'mean': round(float(desc.loc['mean', col]), 4) if col in desc.columns else None,
                    'std': round(float(desc.loc['std', col]), 4) if col in desc.columns else None,
                    'min': round(float(desc.loc['min', col]), 4) if col in desc.columns else None,
                    '25%': round(float(desc.loc['25%', col]), 4) if col in desc.columns else None,
                    '50%': round(float(desc.loc['50%', col]), 4) if col in desc.columns else None,
                    '75%': round(float(desc.loc['75%', col]), 4) if col in desc.columns else None,
                    'max': round(float(desc.loc['max', col]), 4) if col in desc.columns else None,
                    'missing': int(self.df[col].isnull().sum()),
                    'missing_pct': round(float(self.df[col].isnull().sum() / len(self.df) * 100), 2),
                    'unique': int(self.df[col].nunique()),
                    'skewness': round(float(col_data.skew()), 4) if len(col_data) > 2 else None,
                    'kurtosis': round(float(col_data.kurtosis()), 4) if len(col_data) > 3 else None,
                    'variance': round(float(col_data.var()), 4) if len(col_data) > 1 else None,
                    'range': round(float(col_data.max() - col_data.min()), 4) if len(col_data) > 0 else None,
                    'iqr': round(float(col_data.quantile(0.75) - col_data.quantile(0.25)), 4) if len(col_data) > 0 else None
                }
        
        # Categorical column statistics
        for col in self.categorical_cols:
            value_counts = self.df[col].value_counts()
            result['categorical'][col] = {
                'count': int(self.df[col].count()),
                'unique': int(self.df[col].nunique()),
                'top': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                'freq': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                'missing': int(self.df[col].isnull().sum()),
                'missing_pct': round(float(self.df[col].isnull().sum() / len(self.df) * 100), 2),
                'value_counts': {str(k): int(v) for k, v in value_counts.head(10).items()}
            }
        
        # DateTime column statistics
        for col in self.datetime_cols:
            col_data = self.df[col].dropna()
            result['datetime'][col] = {
                'count': int(col_data.count()),
                'min': str(col_data.min()) if len(col_data) > 0 else None,
                'max': str(col_data.max()) if len(col_data) > 0 else None,
                'range_days': int((col_data.max() - col_data.min()).days) if len(col_data) > 0 else None,
                'missing': int(self.df[col].isnull().sum()),
                'missing_pct': round(float(self.df[col].isnull().sum() / len(self.df) * 100), 2)
            }
        
        return result
    
    def get_correlation_matrix(self, method: str = 'pearson') -> Dict[str, Any]:
        """
        Calculate correlation matrix for numeric columns
        Methods: pearson, spearman, kendall
        """
        if not self.numeric_cols or len(self.numeric_cols) < 2:
            return {
                'matrix': {},
                'columns': [],
                'method': method,
                'message': 'Not enough numeric columns for correlation analysis'
            }
        
        corr_matrix = self.df[self.numeric_cols].corr(method=method)
        
        # Convert to serializable format
        matrix_dict = {}
        for col in corr_matrix.columns:
            matrix_dict[col] = {
                row: round(float(corr_matrix.loc[row, col]), 4) if not pd.isna(corr_matrix.loc[row, col]) else None
                for row in corr_matrix.index
            }
        
        # Find top correlations (excluding self-correlations)
        correlations = []
        for i, col1 in enumerate(self.numeric_cols):
            for col2 in self.numeric_cols[i+1:]:
                corr_val = corr_matrix.loc[col1, col2]
                if not pd.isna(corr_val):
                    correlations.append({
                        'column1': col1,
                        'column2': col2,
                        'correlation': round(float(corr_val), 4),
                        'strength': self._correlation_strength(corr_val)
                    })
        
        # Sort by absolute correlation value
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return {
            'matrix': matrix_dict,
            'columns': self.numeric_cols,
            'method': method,
            'top_correlations': correlations[:10],
            'heatmap_data': self._prepare_heatmap_data(corr_matrix)
        }
    
    def _correlation_strength(self, corr: float) -> str:
        """Categorize correlation strength"""
        abs_corr = abs(corr)
        if abs_corr >= 0.8:
            return 'very_strong'
        elif abs_corr >= 0.6:
            return 'strong'
        elif abs_corr >= 0.4:
            return 'moderate'
        elif abs_corr >= 0.2:
            return 'weak'
        return 'very_weak'
    
    def _prepare_heatmap_data(self, corr_matrix: pd.DataFrame) -> List[Dict]:
        """Prepare correlation data for heatmap visualization"""
        heatmap_data = []
        for col in corr_matrix.columns:
            for row in corr_matrix.index:
                val = corr_matrix.loc[row, col]
                if not pd.isna(val):
                    heatmap_data.append({
                        'x': col,
                        'y': row,
                        'value': round(float(val), 4)
                    })
        return heatmap_data
    
    def get_distribution_analysis(self, column: Optional[str] = None, bins: int = 20) -> Dict[str, Any]:
        """
        Analyze distribution of numeric columns
        Returns histogram data, normality tests, and distribution metrics
        """
        columns_to_analyze = [column] if column else self.numeric_cols
        columns_to_analyze = [c for c in columns_to_analyze if c in self.numeric_cols]
        
        if not columns_to_analyze:
            return {
                'distributions': {},
                'message': 'No numeric columns to analyze'
            }
        
        result = {'distributions': {}}
        
        for col in columns_to_analyze:
            col_data = self.df[col].dropna()
            
            if len(col_data) < 3:
                result['distributions'][col] = {
                    'message': 'Not enough data points for distribution analysis'
                }
                continue
            
            # Calculate histogram
            hist_values, bin_edges = np.histogram(col_data, bins=bins)
            histogram_data = [
                {
                    'bin_start': round(float(bin_edges[i]), 4),
                    'bin_end': round(float(bin_edges[i + 1]), 4),
                    'count': int(hist_values[i]),
                    'bin_center': round(float((bin_edges[i] + bin_edges[i + 1]) / 2), 4)
                }
                for i in range(len(hist_values))
            ]
            
            # Calculate box plot data
            q1 = float(col_data.quantile(0.25))
            q3 = float(col_data.quantile(0.75))
            iqr = q3 - q1
            whisker_low = max(float(col_data.min()), q1 - 1.5 * iqr)
            whisker_high = min(float(col_data.max()), q3 + 1.5 * iqr)
            
            # Detect outliers
            outliers = col_data[(col_data < whisker_low) | (col_data > whisker_high)].tolist()
            
            # Normality tests
            normality = {}
            if len(col_data) >= 8 and len(col_data) <= 5000:
                try:
                    stat, p_value = stats.shapiro(col_data.sample(min(5000, len(col_data))))
                    normality['shapiro'] = {
                        'statistic': round(float(stat), 4),
                        'p_value': round(float(p_value), 6),
                        'is_normal': p_value > 0.05
                    }
                except:
                    pass
            
            if len(col_data) >= 20:
                try:
                    stat, p_value = stats.normaltest(col_data)
                    normality['dagostino'] = {
                        'statistic': round(float(stat), 4),
                        'p_value': round(float(p_value), 6),
                        'is_normal': p_value > 0.05
                    }
                except:
                    pass
            
            result['distributions'][col] = {
                'histogram': histogram_data,
                'box_plot': {
                    'min': round(float(col_data.min()), 4),
                    'q1': round(q1, 4),
                    'median': round(float(col_data.median()), 4),
                    'q3': round(q3, 4),
                    'max': round(float(col_data.max()), 4),
                    'whisker_low': round(whisker_low, 4),
                    'whisker_high': round(whisker_high, 4),
                    'iqr': round(iqr, 4),
                    'outliers_count': len(outliers),
                    'outliers_sample': [round(float(o), 4) for o in outliers[:20]]
                },
                'normality_tests': normality,
                'skewness': round(float(col_data.skew()), 4),
                'kurtosis': round(float(col_data.kurtosis()), 4),
                'is_symmetric': abs(float(col_data.skew())) < 0.5,
                'distribution_type': self._infer_distribution_type(col_data)
            }
        
        return result
    
    def _infer_distribution_type(self, data: pd.Series) -> str:
        """Infer the likely distribution type based on data characteristics"""
        skew = float(data.skew())
        kurt = float(data.kurtosis())
        
        if abs(skew) < 0.5 and abs(kurt) < 1:
            return 'approximately_normal'
        elif skew > 1:
            return 'right_skewed'
        elif skew < -1:
            return 'left_skewed'
        elif kurt > 1:
            return 'heavy_tailed'
        elif kurt < -1:
            return 'light_tailed'
        return 'unknown'
    
    def get_chart_data(self, chart_type: str, x_column: Optional[str] = None, 
                       y_column: Optional[str] = None, color_by: Optional[str] = None,
                       limit: int = 1000) -> Dict[str, Any]:
        """
        Generate data for various chart types
        Supported: scatter, line, bar, pie, histogram, box, heatmap
        """
        df_limited = self.df.head(limit)
        
        if chart_type == 'scatter':
            return self._scatter_data(df_limited, x_column, y_column, color_by)
        elif chart_type == 'line':
            return self._line_data(df_limited, x_column, y_column)
        elif chart_type == 'bar':
            return self._bar_data(df_limited, x_column, y_column)
        elif chart_type == 'pie':
            return self._pie_data(df_limited, x_column)
        elif chart_type == 'histogram':
            return self._histogram_data(df_limited, x_column)
        elif chart_type == 'box':
            return self._box_data(df_limited, y_column)
        elif chart_type == 'heatmap':
            return self._heatmap_data(df_limited)
        else:
            return {'error': f'Unsupported chart type: {chart_type}'}
    
    def _scatter_data(self, df: pd.DataFrame, x: str, y: str, color_by: str = None) -> Dict:
        """Generate scatter plot data"""
        if not x or not y:
            # Auto-select first two numeric columns
            if len(self.numeric_cols) >= 2:
                x, y = self.numeric_cols[0], self.numeric_cols[1]
            else:
                return {'error': 'Need at least 2 numeric columns for scatter plot'}
        
        data = []
        for _, row in df[[x, y] + ([color_by] if color_by else [])].dropna().iterrows():
            point = {'x': float(row[x]), 'y': float(row[y])}
            if color_by:
                point['category'] = str(row[color_by])
            data.append(point)
        
        return {
            'type': 'scatter',
            'x_column': x,
            'y_column': y,
            'color_by': color_by,
            'data': data,
            'stats': {
                'correlation': round(float(df[x].corr(df[y])), 4) if len(data) > 1 else None
            }
        }
    
    def _line_data(self, df: pd.DataFrame, x: str, y: str) -> Dict:
        """Generate line chart data"""
        if not x or not y:
            if len(self.numeric_cols) >= 2:
                x, y = self.numeric_cols[0], self.numeric_cols[1]
            elif len(self.numeric_cols) == 1:
                y = self.numeric_cols[0]
                x = None
        
        if x:
            chart_df = df[[x, y]].dropna().sort_values(x)
            data = [{'x': float(row[x]) if pd.api.types.is_numeric_dtype(df[x]) else str(row[x]), 
                    'y': float(row[y])} for _, row in chart_df.iterrows()]
        else:
            data = [{'x': i, 'y': float(v)} for i, v in enumerate(df[y].dropna())]
        
        return {
            'type': 'line',
            'x_column': x or 'index',
            'y_column': y,
            'data': data
        }
    
    def _bar_data(self, df: pd.DataFrame, x: str, y: str = None) -> Dict:
        """Generate bar chart data"""
        if not x:
            x = self.categorical_cols[0] if self.categorical_cols else self.df.columns[0]
        
        if y and y in self.numeric_cols:
            # Aggregate by category
            grouped = df.groupby(x)[y].mean().reset_index()
            data = [{'x': str(row[x]), 'y': round(float(row[y]), 4)} for _, row in grouped.iterrows()]
        else:
            # Value counts
            counts = df[x].value_counts().head(20)
            data = [{'x': str(k), 'y': int(v)} for k, v in counts.items()]
        
        return {
            'type': 'bar',
            'x_column': x,
            'y_column': y or 'count',
            'data': data
        }
    
    def _pie_data(self, df: pd.DataFrame, column: str) -> Dict:
        """Generate pie chart data"""
        if not column:
            column = self.categorical_cols[0] if self.categorical_cols else self.df.columns[0]
        
        counts = df[column].value_counts().head(10)
        total = counts.sum()
        data = [
            {
                'name': str(k),
                'value': int(v),
                'percentage': round(float(v / total * 100), 2)
            }
            for k, v in counts.items()
        ]
        
        return {
            'type': 'pie',
            'column': column,
            'data': data,
            'total': int(total)
        }
    
    def _histogram_data(self, df: pd.DataFrame, column: str, bins: int = 20) -> Dict:
        """Generate histogram data"""
        if not column:
            column = self.numeric_cols[0] if self.numeric_cols else None
        
        if not column or column not in self.numeric_cols:
            return {'error': 'No numeric column specified for histogram'}
        
        col_data = df[column].dropna()
        hist_values, bin_edges = np.histogram(col_data, bins=bins)
        
        data = [
            {
                'bin_start': round(float(bin_edges[i]), 4),
                'bin_end': round(float(bin_edges[i + 1]), 4),
                'count': int(hist_values[i]),
                'x': round(float((bin_edges[i] + bin_edges[i + 1]) / 2), 4)
            }
            for i in range(len(hist_values))
        ]
        
        return {
            'type': 'histogram',
            'column': column,
            'data': data,
            'bins': bins
        }
    
    def _box_data(self, df: pd.DataFrame, columns: str = None) -> Dict:
        """Generate box plot data for numeric columns"""
        cols = [columns] if columns else self.numeric_cols[:10]
        cols = [c for c in cols if c in self.numeric_cols]
        
        if not cols:
            return {'error': 'No numeric columns for box plot'}
        
        data = []
        for col in cols:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                q1 = float(col_data.quantile(0.25))
                q3 = float(col_data.quantile(0.75))
                iqr = q3 - q1
                whisker_low = max(float(col_data.min()), q1 - 1.5 * iqr)
                whisker_high = min(float(col_data.max()), q3 + 1.5 * iqr)
                outliers = col_data[(col_data < whisker_low) | (col_data > whisker_high)]
                
                data.append({
                    'column': col,
                    'min': round(whisker_low, 4),
                    'q1': round(q1, 4),
                    'median': round(float(col_data.median()), 4),
                    'q3': round(q3, 4),
                    'max': round(whisker_high, 4),
                    'outliers': [round(float(o), 4) for o in outliers.head(50).tolist()]
                })
        
        return {
            'type': 'box',
            'data': data
        }
    
    def _heatmap_data(self, df: pd.DataFrame) -> Dict:
        """Generate heatmap data from correlation matrix"""
        if len(self.numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric columns for heatmap'}
        
        corr = df[self.numeric_cols].corr()
        data = []
        
        for i, col1 in enumerate(corr.columns):
            for j, col2 in enumerate(corr.index):
                val = corr.iloc[j, i]
                if not pd.isna(val):
                    data.append({
                        'x': col1,
                        'y': col2,
                        'value': round(float(val), 4)
                    })
        
        return {
            'type': 'heatmap',
            'columns': self.numeric_cols,
            'data': data
        }
    
    def get_column_analysis(self, column: str) -> Dict[str, Any]:
        """Deep analysis of a single column"""
        if column not in self.df.columns:
            return {'error': f'Column {column} not found'}
        
        col_data = self.df[column]
        result = {
            'column': column,
            'dtype': str(col_data.dtype),
            'count': int(col_data.count()),
            'missing': int(col_data.isnull().sum()),
            'missing_pct': round(float(col_data.isnull().sum() / len(self.df) * 100), 2),
            'unique': int(col_data.nunique())
        }
        
        if column in self.numeric_cols:
            col_clean = col_data.dropna()
            result.update({
                'type': 'numeric',
                'mean': round(float(col_clean.mean()), 4),
                'std': round(float(col_clean.std()), 4),
                'min': round(float(col_clean.min()), 4),
                'max': round(float(col_clean.max()), 4),
                'median': round(float(col_clean.median()), 4),
                'q1': round(float(col_clean.quantile(0.25)), 4),
                'q3': round(float(col_clean.quantile(0.75)), 4),
                'skewness': round(float(col_clean.skew()), 4) if len(col_clean) > 2 else None,
                'kurtosis': round(float(col_clean.kurtosis()), 4) if len(col_clean) > 3 else None,
                'zeros': int((col_data == 0).sum()),
                'negatives': int((col_data < 0).sum()),
                'positives': int((col_data > 0).sum())
            })
        elif column in self.categorical_cols:
            value_counts = col_data.value_counts()
            result.update({
                'type': 'categorical',
                'top': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                'freq': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                'value_counts': {str(k): int(v) for k, v in value_counts.head(20).items()}
            })
        
        return result
