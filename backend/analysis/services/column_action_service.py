"""
Column Action Service - Handles individual column actions
"""
import pandas as pd
import os
from django.conf import settings
from analysis.models import TransformationLog


class ColumnActionService:
    """Service for applying actions to individual columns"""
    
    @staticmethod
    def apply_action(df, project, column, action, strategy=None, value=None):
        """
        Apply an action to a specific column
        
        Args:
            df: pandas DataFrame
            project: Project model instance
            column: column name
            action: action type string
            strategy: optional strategy for the action
            value: optional value parameter
            
        Returns:
            tuple (DataFrame, list of changes made)
        """
        original_shape = df.shape
        changes_made = []
        
        action_map = {
            'fill_missing': ColumnActionService._fill_missing,
            'drop_rows': ColumnActionService._drop_rows,
            'remove_outliers': ColumnActionService._remove_outliers,
            'cap_outliers': ColumnActionService._cap_outliers,
            'convert_type': ColumnActionService._convert_type,
            'text_transform': ColumnActionService._text_transform,
            'remove_duplicates': ColumnActionService._remove_duplicates,
        }
        
        handler = action_map.get(action)
        if handler:
            df, changes = handler(df, column, strategy, value)
            changes_made.extend(changes)
        
        return df, changes_made
    
    @staticmethod
    def _fill_missing(df, column, strategy, value):
        """Fill missing values"""
        changes = []
        null_count_before = df[column].isnull().sum()
        
        if strategy == 'mean':
            df[column].fillna(df[column].mean(), inplace=True)
        elif strategy == 'median':
            df[column].fillna(df[column].median(), inplace=True)
        elif strategy == 'mode':
            mode_val = df[column].mode()
            if len(mode_val) > 0:
                df[column].fillna(mode_val[0], inplace=True)
        elif strategy == 'forward_fill':
            df[column].fillna(method='ffill', inplace=True)
        elif strategy == 'backward_fill':
            df[column].fillna(method='bfill', inplace=True)
        elif strategy == 'constant' and value is not None:
            df[column].fillna(value, inplace=True)
        
        null_count_after = df[column].isnull().sum()
        changes.append(f"Filled {null_count_before - null_count_after} missing values using {strategy}")
        
        return df, changes
    
    @staticmethod
    def _drop_rows(df, column, strategy, value):
        """Drop rows with missing values"""
        rows_before = len(df)
        df.dropna(subset=[column], inplace=True)
        rows_after = len(df)
        return df, [f"Dropped {rows_before - rows_after} rows with missing values"]
    
    @staticmethod
    def _remove_outliers(df, column, strategy, value):
        """Remove outliers using IQR method"""
        changes = []
        if strategy == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            rows_before = len(df)
            df = df[(df[column] >= lower) & (df[column] <= upper)]
            rows_after = len(df)
            changes.append(f"Removed {rows_before - rows_after} outliers using IQR method")
        return df, changes
    
    @staticmethod
    def _cap_outliers(df, column, strategy, value):
        """Cap outliers to IQR bounds"""
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        capped_low = (df[column] < lower).sum()
        capped_high = (df[column] > upper).sum()
        df[column] = df[column].clip(lower=lower, upper=upper)
        return df, [f"Capped {capped_low} low values and {capped_high} high values"]
    
    @staticmethod
    def _convert_type(df, column, target_type, value):
        """Convert column data type"""
        changes = []
        if target_type == 'numeric':
            df[column] = pd.to_numeric(df[column], errors='coerce')
            changes.append(f"Converted {column} to numeric type")
        elif target_type == 'datetime':
            df[column] = pd.to_datetime(df[column], errors='coerce')
            changes.append(f"Converted {column} to datetime type")
        elif target_type == 'string':
            df[column] = df[column].astype(str)
            changes.append(f"Converted {column} to string type")
        elif target_type == 'category':
            df[column] = df[column].astype('category')
            changes.append(f"Converted {column} to category type")
        return df, changes
    
    @staticmethod
    def _text_transform(df, column, strategy, value):
        """Apply text transformations"""
        changes = []
        if strategy == 'trim':
            df[column] = df[column].astype(str).str.strip()
            changes.append(f"Trimmed whitespace from {column}")
        elif strategy == 'lowercase':
            df[column] = df[column].astype(str).str.lower()
            changes.append(f"Converted {column} to lowercase")
        elif strategy == 'uppercase':
            df[column] = df[column].astype(str).str.upper()
            changes.append(f"Converted {column} to uppercase")
        elif strategy == 'remove_special':
            df[column] = df[column].astype(str).str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
            changes.append(f"Removed special characters from {column}")
        return df, changes
    
    @staticmethod
    def _remove_duplicates(df, column, strategy, value):
        """Remove duplicate rows"""
        rows_before = len(df)
        if column:
            df.drop_duplicates(subset=[column], keep='first', inplace=True)
        else:
            df.drop_duplicates(keep='first', inplace=True)
        rows_after = len(df)
        return df, [f"Removed {rows_before - rows_after} duplicate rows"]
    
    @staticmethod
    def save_and_log(df, project, column, action, strategy, changes):
        """Save data and create transformation log"""
        processed_path = os.path.join(
            settings.PIPELINE_STORAGE_PATH,
            'processed',
            f"{project.project_id}_processed.csv"
        )
        os.makedirs(os.path.dirname(processed_path), exist_ok=True)
        df.to_csv(processed_path, index=False)
        
        # Log the transformation
        TransformationLog.objects.create(
            project=project,
            step_name='Column Action',
            action=action,
            target=column,
            reason=f"User applied {action} with {strategy or 'default'} strategy",
            impact={'changes': changes},
            confidence=1.0
        )
        
        return processed_path
