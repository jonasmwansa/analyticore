from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .context import PipelineContext, ChangeLogEntry
import logging

logger = logging.getLogger(__name__)

class PipelineStep(ABC):
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.enabled = True
    
    @abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        pass
    
    def validate(self, context: PipelineContext) -> bool:
        return True
    
    def can_skip(self, context: PipelineContext) -> bool:
        return False
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"

class Pipeline:
    def __init__(self, name: str, steps: Optional[List[PipelineStep]] = None):
        self.name = name
        self.steps: List[PipelineStep] = steps or []
        self.logger = logging.getLogger(f"pipeline.{name}")
    
    def add_step(self, step: PipelineStep):
        self.steps.append(step)
        return self
    
    def execute(self, context: PipelineContext, manual_mode: bool = False) -> PipelineContext:
        self.logger.info(f"Starting pipeline '{self.name}' with {len(self.steps)} steps")
        
        for i, step in enumerate(self.steps, 1):
            if not step.enabled:
                self.logger.info(f"Step {i}/{len(self.steps)}: {step.name} - SKIPPED (disabled)")
                continue
            
            if step.can_skip(context):
                self.logger.info(f"Step {i}/{len(self.steps)}: {step.name} - SKIPPED (can_skip)")
                continue
            
            if not step.validate(context):
                self.logger.warning(f"Step {i}/{len(self.steps)}: {step.name} - FAILED validation")
                if not manual_mode:
                    raise ValueError(f"Step {step.name} failed validation")
                continue
            
            try:
                self.logger.info(f"Step {i}/{len(self.steps)}: {step.name} - RUNNING")
                context = step.execute(context)
                self.logger.info(f"Step {i}/{len(self.steps)}: {step.name} - COMPLETED")
            except Exception as e:
                self.logger.error(f"Step {i}/{len(self.steps)}: {step.name} - ERROR: {str(e)}")
                if not manual_mode:
                    raise
                context.log_change(
                    step=step.name,
                    action='error',
                    target='pipeline',
                    reason=f'Step failed: {str(e)}',
                    impact={'error': str(e)},
                    confidence=1.0,
                    reversible=False
                )
        
        self.logger.info(f"Pipeline '{self.name}' completed with {len(context.change_log)} changes")
        return context
    
    def __repr__(self):
        return f"Pipeline(name='{self.name}', steps={len(self.steps)})"