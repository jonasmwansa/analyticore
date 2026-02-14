from .base import PipelineStep
from .context import PipelineContext
import pandas as pd
import numpy as np
from typing import Dict, Any

class ColumnUnderstandingStep(PipelineStep):
    def __init__(self):
        super().__init__("Column Understanding")
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        df = context.current_df
        
        for column in df.columns:
            col_data = df[column]
            
            inferred_type, confidence = self._infer_type(col_data)
            is_identifier = self._is_identifier(col_data)
            
            from pipelines.context import ColumnMetadata
            metadata = ColumnMetadata(
                name=column,
                inferred_type=inferred_type,
                confidence=confidence,
                missing_count=col_data.isna().sum(),
                missing_percentage=(col_data.isna().sum() / len(col_data)) * 100,
                unique_count=col_data.nunique(),
                is_identifier=is_identifier,
                sample_values=col_data.dropna().head(5).tolist(),
                statistics=self._get_column_stats(col_data, inferred_type)
            )
            
            context.metadata[column] = metadata
            
            context.log_change(
                step=self.name,
                action='infer_type',
                target=column,
                reason=f'Inferred type as {inferred_type}',
                impact={'type': inferred_type, 'confidence': confidence},
                confidence=confidence
            )
        
        return context
    
    def _infer_type(self, col_data: pd.Series) -> tuple:
        non_null = col_data.dropna()
        if len(non_null) == 0:
            return 'unknown', 0.0
        
        if pd.api.types.is_numeric_dtype(col_data):
            if col_data.dtype == 'int64' and col_data.nunique() < len(col_data) * 0.5:
                return 'categorical', 0.8
            return 'numeric', 0.95
        
        try:
            pd.to_datetime(non_null, errors='raise')
            return 'datetime', 0.9
        except:
            pass
        
        if col_data.nunique() / len(col_data) < 0.05:
            return 'categorical', 0.85
        
        return 'text', 0.7
    
    def _is_identifier(self, col_data: pd.Series) -> bool:
        if len(col_data) == 0:
            return False
        unique_ratio = col_data.nunique() / len(col_data)
        return unique_ratio > 0.95
    
    def _get_column_stats(self, col_data: pd.Series, col_type: str) -> Dict[str, Any]:
        stats = {}
        if col_type == 'numeric':
            stats = {
                'mean': float(col_data.mean()) if not col_data.isna().all() else None,
                'median': float(col_data.median()) if not col_data.isna().all() else None,
                'std': float(col_data.std()) if not col_data.isna().all() else None,
                'min': float(col_data.min()) if not col_data.isna().all() else None,
                'max': float(col_data.max()) if not col_data.isna().all() else None,
            }
        elif col_type == 'categorical':
            value_counts = col_data.value_counts()
            stats = {
                'top_values': value_counts.head(10).to_dict(),
                'category_count': len(value_counts)
            }
        return stats