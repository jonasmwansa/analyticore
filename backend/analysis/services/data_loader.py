"""
Data Loader Service - Handles loading project data into DataFrames
"""
import pandas as pd
import os


class DataLoaderService:
    """Service for loading project data into pandas DataFrames"""
    
    @staticmethod
    def load_dataframe(project):
        """
        Load project data into a DataFrame
        
        Args:
            project: Project model instance
            
        Returns:
            pandas.DataFrame or None if loading fails
        """
        file_path = project.processed_file_path or project.file_path
        
        if not file_path or not os.path.exists(file_path):
            return None
        
        return DataLoaderService._load_file(file_path)
    
    @staticmethod
    def _load_file(file_path):
        """Load file based on extension"""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            return pd.read_json(file_path)
        return None
    
    @staticmethod
    def get_column_types(df):
        """
        Categorize columns by their data types
        
        Args:
            df: pandas DataFrame
            
        Returns:
            dict with numeric, categorical, datetime columns
        """
        import numpy as np
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        return {
            'numeric': numeric_cols,
            'categorical': categorical_cols,
            'datetime': datetime_cols
        }
    
    @staticmethod
    def get_columns_info(df):
        """
        Get detailed column information
        
        Args:
            df: pandas DataFrame
            
        Returns:
            list of column info dicts
        """
        column_types = DataLoaderService.get_column_types(df)
        
        columns = []
        for col in df.columns:
            if col in column_types['numeric']:
                col_type = 'numeric'
            elif col in column_types['datetime']:
                col_type = 'datetime'
            else:
                col_type = 'categorical'
            
            columns.append({
                'name': col,
                'type': col_type,
                'dtype': str(df[col].dtype)
            })
        
        return columns
