"""
Executor Class Wrapper

Provides a class-based interface to executor functions.
"""

import logging
from sentinel_core.executor import executor
from sentinel_core.models.planner import PlanSchema
from sentinel_core.models.executor import ExecutionResult
from typing import Optional, List
from sqlmodel import Session

logger = logging.getLogger(__name__)


class Executor:
    """
    Class-based wrapper around executor functions.
    
    Makes the executor easier to use in pipelines that expect
    class-based components.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the executor.
        
        Args:
            db_session: Optional database session for logging
        """
        self.db_session = db_session
    
    async def execute_plan(
        self,
        plan: PlanSchema,
        approved_actions: Optional[List[int]] = None,
        dry_run: bool = True
    ) -> ExecutionResult:
        """
        Execute a validated plan.
        
        Args:
            plan: The plan to execute
            approved_actions: Optional list of action indices to execute
            dry_run: If True, only simulate execution
            
        Returns:
            ExecutionResult with operation outcomes
        """
        logger.info(f"[Executor] execute_plan called: dry_run={dry_run}, plan type={type(plan).__name__}")
        logger.info(f"[Executor] plan has {len(plan.actions)} actions, {len(plan.folders_to_create)} folders")
        
        if plan.actions:
            first = plan.actions[0]
            logger.info(f"[Executor] First action: type={first.type}, source={first.source_path}, dest={first.destination_path}")
        
        if dry_run:
            logger.info("[Executor] DRY RUN — simulating execution, no files will be moved")
            return ExecutionResult(
                task_id=plan.task_id,
                total_actions=len(plan.actions),
                successful_actions=len(plan.actions),
                failed_actions=0,
                execution_logs=[],
                error_message=None,
                rollback_performed=False
            )
        else:
            logger.info("[Executor] REAL EXECUTION — calling module executor to move files")
            result = executor.execute_plan(
                plan=plan,
                approved_actions=approved_actions,
                db_session=self.db_session
            )
            logger.info(f"[Executor] Result: {result.successful_actions} succeeded, {result.failed_actions} failed, error={result.error_message}")
            return result
