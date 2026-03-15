"""
Smart Chart Recommendation Engine - Intelligently recommends chart types based on data characteristics
Uses both rule-based analysis and local LLM for dynamic, generative recommendations
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ChartType(Enum):
    # Single variable charts
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    VIOLIN_PLOT = "violin_plot"
    KDE_PLOT = "kde_plot"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    DONUT_CHART = "donut_chart"
    TREEMAP = "treemap"
    
    # Two variable charts
    SCATTER_PLOT = "scatter_plot"
    LINE_CHART = "line_chart"
    AREA_CHART = "area_chart"
    BUBBLE_CHART = "bubble_chart"
    GROUPED_BAR = "grouped_bar_chart"
    STACKED_BAR = "stacked_bar_chart"
    HEATMAP = "heatmap"
    
    # Multi-variable charts
    CORRELATION_MATRIX = "correlation_matrix"
    PARALLEL_COORDINATES = "parallel_coordinates"
    RADAR_CHART = "radar_chart"
    PAIR_PLOT = "pair_plot"
    
    # Time series charts
    TIME_SERIES = "time_series"
    CANDLESTICK = "candlestick"
    SPARKLINE = "sparkline"
    
    # Specialized charts
    FUNNEL = "funnel_chart"
    SANKEY = "sankey_diagram"
    WORD_CLOUD = "word_cloud"


@dataclass
class ColumnProfile:
    """Profile of a single column"""
    name: str
    dtype: str
    is_numeric: bool
    is_categorical: bool
    is_datetime: bool
    is_text: bool
    unique_count: int
    unique_ratio: float
    missing_count: int
    missing_ratio: float
    cardinality: str  # 'low', 'medium', 'high', 'unique'
    distribution: Optional[str] = None  # 'normal', 'skewed', 'bimodal', 'uniform'
    stats: Optional[Dict] = None


@dataclass
class ChartRecommendation:
    """A chart recommendation with reasoning"""
    chart_type: ChartType
    title: str
    description: str
    columns: List[str]
    priority: int  # 1-10, higher is more recommended
    reasoning: str
    config: Dict[str, Any]
    data_requirements: Dict[str, Any]


class ChartRecommendationEngine:
    """
    Analyzes data characteristics and recommends appropriate visualizations
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.profiles: Dict[str, ColumnProfile] = {}
        self._analyze_columns()
    
    def _analyze_columns(self):
        """Analyze each column and create profiles"""
        for col in self.df.columns:
            series = self.df[col]
            
            # Determine data type
            is_numeric = pd.api.types.is_numeric_dtype(series)
            is_datetime = pd.api.types.is_datetime64_any_dtype(series)
            is_categorical = pd.api.types.is_categorical_dtype(series) or (
                series.dtype == 'object' and series.nunique() < len(series) * 0.5
            )
            is_text = series.dtype == 'object' and series.str.len().mean() > 50 if series.dtype == 'object' else False
            
            # Calculate metrics
            unique_count = series.nunique()
            unique_ratio = unique_count / len(series) if len(series) > 0 else 0
            missing_count = series.isnull().sum()
            missing_ratio = missing_count / len(series) if len(series) > 0 else 0
            
            # Determine cardinality
            if unique_ratio > 0.9:
                cardinality = 'unique'
            elif unique_count <= 5:
                cardinality = 'low'
            elif unique_count <= 20:
                cardinality = 'medium'
            else:
                cardinality = 'high'
            
            # Analyze distribution for numeric columns
            distribution = None
            stats = None
            if is_numeric and not series.isnull().all():
                clean_series = series.dropna()
                if len(clean_series) > 10:
                    skewness = clean_series.skew()
                    kurtosis = clean_series.kurtosis()
                    
                    if abs(skewness) < 0.5 and abs(kurtosis) < 1:
                        distribution = 'normal'
                    elif abs(skewness) > 1:
                        distribution = 'skewed'
                    elif kurtosis < -1:
                        distribution = 'bimodal'
                    else:
                        distribution = 'uniform'
                    
                    stats = {
                        'mean': float(clean_series.mean()),
                        'std': float(clean_series.std()),
                        'min': float(clean_series.min()),
                        'max': float(clean_series.max()),
                        'median': float(clean_series.median()),
                        'skewness': float(skewness),
                        'kurtosis': float(kurtosis)
                    }
            
            self.profiles[col] = ColumnProfile(
                name=col,
                dtype=str(series.dtype),
                is_numeric=is_numeric,
                is_categorical=is_categorical,
                is_datetime=is_datetime,
                is_text=is_text,
                unique_count=unique_count,
                unique_ratio=unique_ratio,
                missing_count=missing_count,
                missing_ratio=missing_ratio,
                cardinality=cardinality,
                distribution=distribution,
                stats=stats
            )
    
    def get_recommendations(self, max_recommendations: int = 10) -> List[ChartRecommendation]:
        """Generate chart recommendations based on data analysis"""
        recommendations = []
        
        numeric_cols = [p.name for p in self.profiles.values() if p.is_numeric]
        categorical_cols = [p.name for p in self.profiles.values() if p.is_categorical]
        datetime_cols = [p.name for p in self.profiles.values() if p.is_datetime]
        
        # 1. Single numeric column distributions
        for col in numeric_cols[:3]:
            profile = self.profiles[col]
            
            # Histogram for distributions
            recommendations.append(ChartRecommendation(
                chart_type=ChartType.HISTOGRAM,
                title=f"Distribution of {col}",
                description=f"Shows the frequency distribution of {col} values",
                columns=[col],
                priority=8,
                reasoning=f"Histograms are ideal for understanding the distribution of numeric data. {col} has {profile.distribution or 'varied'} distribution.",
                config={'bins': 'auto', 'show_kde': True},
                data_requirements={'min_rows': 20, 'type': 'numeric'}
            ))
            
            # Box plot for outliers
            if profile.distribution == 'skewed':
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.BOX_PLOT,
                    title=f"Box Plot of {col}",
                    description=f"Identifies outliers and quartile distribution in {col}",
                    columns=[col],
                    priority=7,
                    reasoning=f"{col} appears skewed, making box plots valuable for identifying outliers and understanding the spread.",
                    config={'show_outliers': True, 'show_mean': True},
                    data_requirements={'min_rows': 10, 'type': 'numeric'}
                ))
        
        # 2. Categorical distributions
        for col in categorical_cols[:3]:
            profile = self.profiles[col]
            
            if profile.cardinality == 'low':
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.PIE_CHART,
                    title=f"Distribution of {col}",
                    description=f"Shows proportion of each {col} category",
                    columns=[col],
                    priority=7 if profile.unique_count <= 5 else 5,
                    reasoning=f"Pie charts work well with {profile.unique_count} categories. Shows relative proportions clearly.",
                    config={'show_percentage': True, 'show_labels': True},
                    data_requirements={'max_categories': 7, 'type': 'categorical'}
                ))
            else:
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.BAR_CHART,
                    title=f"Frequency of {col}",
                    description=f"Shows count of each {col} category",
                    columns=[col],
                    priority=8,
                    reasoning=f"Bar charts handle {profile.unique_count} categories well and allow easy comparison.",
                    config={'orientation': 'horizontal' if profile.unique_count > 6 else 'vertical', 'sort': True},
                    data_requirements={'type': 'categorical'}
                ))
        
        # 3. Numeric vs Numeric relationships
        if len(numeric_cols) >= 2:
            # Scatter plot for correlations
            for i, col1 in enumerate(numeric_cols[:3]):
                for col2 in numeric_cols[i+1:4]:
                    corr = self.df[col1].corr(self.df[col2])
                    if abs(corr) > 0.3:
                        recommendations.append(ChartRecommendation(
                            chart_type=ChartType.SCATTER_PLOT,
                            title=f"{col1} vs {col2}",
                            description=f"Relationship between {col1} and {col2} (correlation: {corr:.2f})",
                            columns=[col1, col2],
                            priority=9 if abs(corr) > 0.6 else 6,
                            reasoning=f"These columns have {'strong' if abs(corr) > 0.6 else 'moderate'} correlation ({corr:.2f}). Scatter plot reveals the relationship pattern.",
                            config={'show_trendline': True, 'correlation': round(corr, 3)},
                            data_requirements={'min_rows': 30, 'type': 'numeric_pair'}
                        ))
            
            # Correlation heatmap
            if len(numeric_cols) >= 3:
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.CORRELATION_MATRIX,
                    title="Correlation Heatmap",
                    description="Shows relationships between all numeric variables",
                    columns=numeric_cols[:10],
                    priority=9,
                    reasoning="With multiple numeric columns, a correlation heatmap provides a comprehensive view of all relationships.",
                    config={'cmap': 'RdBu_r', 'annotate': len(numeric_cols) <= 8},
                    data_requirements={'min_columns': 3, 'type': 'numeric_multi'}
                ))
        
        # 4. Categorical vs Numeric
        for cat_col in categorical_cols[:2]:
            cat_profile = self.profiles[cat_col]
            if cat_profile.cardinality in ['low', 'medium']:
                for num_col in numeric_cols[:2]:
                    recommendations.append(ChartRecommendation(
                        chart_type=ChartType.GROUPED_BAR,
                        title=f"{num_col} by {cat_col}",
                        description=f"Compare {num_col} across {cat_col} categories",
                        columns=[cat_col, num_col],
                        priority=7,
                        reasoning=f"Grouped bar chart shows how {num_col} varies across the {cat_profile.unique_count} categories of {cat_col}.",
                        config={'aggregation': 'mean', 'show_error_bars': True},
                        data_requirements={'type': 'categorical_numeric'}
                    ))
                    
                    recommendations.append(ChartRecommendation(
                        chart_type=ChartType.BOX_PLOT,
                        title=f"{num_col} Distribution by {cat_col}",
                        description=f"Compare distribution of {num_col} across {cat_col} groups",
                        columns=[cat_col, num_col],
                        priority=8,
                        reasoning=f"Box plots by category reveal distribution differences and outliers across {cat_col} groups.",
                        config={'show_outliers': True, 'orientation': 'horizontal'},
                        data_requirements={'type': 'categorical_numeric'}
                    ))
        
        # 5. Time series analysis
        for dt_col in datetime_cols:
            for num_col in numeric_cols[:2]:
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.TIME_SERIES,
                    title=f"{num_col} Over Time",
                    description=f"Trend of {num_col} across {dt_col}",
                    columns=[dt_col, num_col],
                    priority=9,
                    reasoning="Time series visualization reveals trends, seasonality, and patterns over time.",
                    config={'show_trend': True, 'show_moving_average': True},
                    data_requirements={'type': 'time_series'}
                ))
        
        # 6. Multi-variable analysis
        if len(numeric_cols) >= 4:
            recommendations.append(ChartRecommendation(
                chart_type=ChartType.PAIR_PLOT,
                title="Pair Plot Matrix",
                description="Comprehensive view of all numeric variable relationships",
                columns=numeric_cols[:5],
                priority=7,
                reasoning="Pair plots provide a complete picture of relationships between multiple variables simultaneously.",
                config={'diag_kind': 'kde'},
                data_requirements={'min_columns': 4, 'max_columns': 6, 'type': 'numeric_multi'}
            ))
        
        # Sort by priority and return top recommendations
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        return recommendations[:max_recommendations]
    
    def get_recommendation_summary(self) -> Dict[str, Any]:
        """Get a summary of column profiles and recommendations"""
        recommendations = self.get_recommendations()
        
        return {
            'column_profiles': {
                name: {
                    'type': profile.dtype,
                    'is_numeric': profile.is_numeric,
                    'is_categorical': profile.is_categorical,
                    'is_datetime': profile.is_datetime,
                    'cardinality': profile.cardinality,
                    'distribution': profile.distribution,
                    'unique_count': profile.unique_count,
                    'missing_ratio': round(profile.missing_ratio, 3)
                }
                for name, profile in self.profiles.items()
            },
            'recommendations': [
                {
                    'chart_type': rec.chart_type.value,
                    'title': rec.title,
                    'description': rec.description,
                    'columns': rec.columns,
                    'priority': rec.priority,
                    'reasoning': rec.reasoning,
                    'config': rec.config
                }
                for rec in recommendations
            ],
            'data_summary': {
                'total_rows': len(self.df),
                'total_columns': len(self.df.columns),
                'numeric_columns': len([p for p in self.profiles.values() if p.is_numeric]),
                'categorical_columns': len([p for p in self.profiles.values() if p.is_categorical]),
                'datetime_columns': len([p for p in self.profiles.values() if p.is_datetime]),
                'best_chart_types': list(set([r.chart_type.value for r in recommendations[:5]]))
            }
        }


def get_smart_chart_recommendations(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Main function to get intelligent chart recommendations for a dataframe
    """
    engine = ChartRecommendationEngine(df)
    return engine.get_recommendation_summary()
