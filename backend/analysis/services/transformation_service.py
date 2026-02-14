"""
Transformation Service - Handles data transformations
"""
import pandas as pd
import os
from django.conf import settings
from analysis.models import TransformationLog


class TransformationService:
    """Service for applying data transformations"""
    
    @staticmethod
    def apply_rules(df, rules, project):
        """
        Apply a list of transformation rules to a DataFrame
        
        Args:
            df: pandas DataFrame
            rules: list of transformation rule dicts
            project: Project model instance
            
        Returns:
            tuple (transformed DataFrame, list of applied transformations)
        """
        original_shape = df.shape
        applied = []
        
        for rule in rules:
            column = rule.get('column')
            action = rule.get('action')
            params = rule.get('parameters', {})
            
            df = TransformationService._apply_single_rule(df, column, action, params)
            
            # Log the transformation
            TransformationLog.objects.create(
                project=project,
                step_name='User Applied',
                action=action,
                target=column,
                reason=rule.get('recommendation', 'User applied transformation'),
                impact={'before': original_shape, 'after': df.shape},
                confidence=1.0
            )
            
            applied.append(rule)
        
        return df, applied
    
    @staticmethod
    def _apply_single_rule(df, column, action, params):
        """Apply a single transformation rule"""
        
        if action == 'fill_missing':
            df = TransformationService._fill_missing(df, column, params)
        elif action == 'remove_duplicates':
            df.drop_duplicates(inplace=True)
        elif action == 'convert_type':
            df = TransformationService._convert_type(df, column, params)
        elif action == 'remove_outliers':
            df = TransformationService._remove_outliers(df, column)
        elif action == 'rename_column':
            new_name = params.get('new_name')
            if new_name:
                df.rename(columns={column: new_name}, inplace=True)
        
        return df
    
    @staticmethod
    def _fill_missing(df, column, params):
        """Fill missing values based on strategy"""
        strategy = params.get('strategy', 'mean')
        
        if strategy == 'mean' and df[column].dtype in ['int64', 'float64']:
            df[column].fillna(df[column].mean(), inplace=True)
        elif strategy == 'median' and df[column].dtype in ['int64', 'float64']:
            df[column].fillna(df[column].median(), inplace=True)
        elif strategy == 'mode':
            mode_val = df[column].mode()
            if len(mode_val) > 0:
                df[column].fillna(mode_val[0], inplace=True)
        elif strategy == 'forward_fill':
            df[column].fillna(method='ffill', inplace=True)
        elif strategy == 'constant':
            df[column].fillna(params.get('value', 0), inplace=True)
        
        return df
    
    @staticmethod
    def _convert_type(df, column, params):
        """Convert column to specified type"""
        target_type = params.get('target_type')
        
        if target_type == 'numeric':
            df[column] = pd.to_numeric(df[column], errors='coerce')
        elif target_type == 'datetime':
            df[column] = pd.to_datetime(df[column], errors='coerce')
        elif target_type == 'string':
            df[column] = df[column].astype(str)
        
        return df
    
    @staticmethod
    def _remove_outliers(df, column):
        """Remove outliers using IQR method"""
        if df[column].dtype in ['int64', 'float64']:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            df = df[(df[column] >= lower) & (df[column] <= upper)]
        return df
    
    @staticmethod
    def save_processed_data(df, project_id):
        """
        Save processed DataFrame to file
        
        Args:
            df: pandas DataFrame
            project_id: UUID of the project
            
        Returns:
            str: path to saved file
        """
        processed_path = os.path.join(
            settings.PIPELINE_STORAGE_PATH,
            'processed',
            f"{project_id}_processed.csv"
        )
        os.makedirs(os.path.dirname(processed_path), exist_ok=True)
        df.to_csv(processed_path, index=False)
        return processed_path
