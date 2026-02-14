from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime

@dataclass
class ColumnMetadata:
    name: str
    inferred_type: str
    confidence: float
    missing_count: int
    missing_percentage: float
    unique_count: int
    is_identifier: bool
    sample_values: List[Any] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChangeLogEntry:
    timestamp: datetime
    step: str
    action: str
    target: str
    reason: str
    impact: Dict[str, Any]
    confidence: float
    reversible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PipelineContext:
    project_id: str
    original_df: pd.DataFrame
    current_df: pd.DataFrame
    metadata: Dict[str, ColumnMetadata] = field(default_factory=dict)
    change_log: List[ChangeLogEntry] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    
    def log_change(self, step: str, action: str, target: str, reason: str, 
                   impact: Dict[str, Any], confidence: float, **kwargs):
        entry = ChangeLogEntry(
            timestamp=datetime.now(),
            step=step,
            action=action,
            target=target,
            reason=reason,
            impact=impact,
            confidence=confidence,
            **kwargs
        )
        self.change_log.append(entry)
        return entry
    
    def get_changes_by_step(self, step: str) -> List[ChangeLogEntry]:
        return [entry for entry in self.change_log if entry.step == step]
    
    def get_changes_by_target(self, target: str) -> List[ChangeLogEntry]:
        return [entry for entry in self.change_log if entry.target == target]