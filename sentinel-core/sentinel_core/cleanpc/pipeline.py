"""
Clean My PC Pipeline

Main orchestrator for the Clean My PC feature.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from sentinel_core.scanner.scanner import Scanner
from sentinel_core.models.filesystem import ScanResult, FileMetadata
from sentinel_core.models.preferences import PreferencesSchema
from sentinel_core.cleanpc.classifiers import FileClassifier, FileClassification
from sentinel_core.cleanpc.rules import OrganizationRules
from sentinel_core.planner.planner_agent import PlannerAgent
from sentinel_core.safety.safety import SafetyValidator
from sentinel_core.executor import Executor
from sentinel_core.models.planner import PlanSchema

logger = logging.getLogger(__name__)


class CleanPCPipeline:
    """
    Orchestrates the Clean My PC workflow.
    
    This pipeline:
    1. Scans target directories (Downloads, Desktop, Documents, Videos)
    2. Classifies files using heuristics
    3. Applies organization rules
    4. Generates an AI-assisted plan
    5. Validates for safety
    6. Returns plan for user approval
    
    Execution happens separately after user approval.
    """
    
    def __init__(
        self,
        planner: PlannerAgent,
        safety: SafetyValidator,
        executor: Executor
    ):
        """
        Initialize the pipeline.
        
        Args:
            planner: Planner agent for generating organization plans
            safety: Safety validator for checking plans
            executor: Executor for carrying out approved operations
        """
        self.planner = planner
        self.safety = safety
        self.executor = executor
        self.classifier = FileClassifier()
        self.rules = OrganizationRules()
    
    async def scan_and_plan(
        self,
        task_id: str,
        target_dirs: Optional[List[str]] = None,
        preferences: Optional[PreferencesSchema] = None,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Scan directories and generate a cleanup plan.
        
        This is the main entry point. It performs scanning and planning,
        but does NOT execute. Execution requires separate user approval.
        
        Args:
            task_id: Unique task identifier
            target_dirs: Directories to scan (default: standard user dirs)
            preferences: User preferences
            max_depth: Maximum directory depth to scan
            
        Returns:
            Dictionary containing:
                - task_id: Task identifier
                - plan: Generated plan
                - summary: Statistics about found files
                - classifications: List of file classifications
        """
        logger.info(f"Starting Clean My PC pipeline for task {task_id}")
        
        # 1. Define target directories
        if target_dirs is None:
            target_dirs = self._get_default_target_dirs()
        
        logger.info(f"Scanning directories: {target_dirs}")
        
        # 2. Scan all directories
        all_files: List[FileMetadata] = []
        scan_errors: List[str] = []
        
        for dir_path in target_dirs:
            try:
                scanner = Scanner(dir_path, max_depth=max_depth)
                scan_result = scanner.scan()
                all_files.extend(scan_result.files)
                scan_errors.extend(scan_result.errors)
            except Exception as e:
                logger.error(f"Failed to scan {dir_path}: {e}")
                scan_errors.append(f"Failed to scan {dir_path}: {str(e)}")
        
        logger.info(f"Scanned {len(all_files)} files")
        
        # 3. Classify files
        logger.info("Classifying files...")
        classifications = self.classifier.classify_all(all_files)
        
        # 4. Apply organization rules
        logger.info("Applying organization rules...")
        rule_matches = self.rules.apply_rules(classifications)
        
        logger.info(f"Found {len(rule_matches)} rule matches")
        
        # 5. Create combined scan result for planner
        combined_scan = ScanResult(
            root_path=", ".join(target_dirs),
            files=all_files,
            errors=scan_errors
        )
        
        # 6. Generate AI plan
        logger.info("Generating AI plan...")
        
        # Use default preferences if none provided
        if preferences is None:
            preferences = PreferencesSchema()
        
        try:
            plan = self.planner.create_plan(
                task_id=task_id,
                scan_result=combined_scan,
                rule_matches=rule_matches,
                preferences=preferences
            )
        except Exception as e:
            logger.error(f"Failed to generate plan: {e}")
            # Fallback: create a simple plan from rule matches
            plan = self._create_fallback_plan(task_id, rule_matches, classifications)
        
        # 7. Safety validation
        logger.info("Validating plan for safety...")
        validation_result = self.safety.validate_plan(plan)
        
        if not validation_result.is_safe:
            logger.warning(f"AI plan failed safety validation: {validation_result.errors}")
            logger.info("Falling back to rule-based plan...")
            
            # Try fallback plan instead of aborting
            plan = self._create_fallback_plan(task_id, rule_matches, classifications)
            
            logger.info(f"Fallback plan created with {len(plan.actions)} actions, {len(plan.folders_to_create)} folders")
            
            # Validate fallback plan
            validation_result = self.safety.validate_plan(plan)
            
            logger.info(f"Fallback validation: is_safe={validation_result.is_safe}, errors={validation_result.errors}")
            
            if not validation_result.is_safe:
                logger.error(f"Fallback plan also failed safety validation: {validation_result.errors}")
                raise ValueError(
                    f"Plan failed safety validation: {'; '.join(validation_result.errors)}"
                )
        
        # 8. Log warnings if any
        if validation_result.warnings:
            logger.warning(f"Plan warnings: {validation_result.warnings}")
        
        # 9. Generate summary statistics
        summary = self._generate_summary(classifications, plan)
        
        logger.info(f"Clean My PC scan complete. Found {summary['total_files']} files, "
                   f"{len(plan.actions)} operations planned")
        
        return {
            "task_id": task_id,
            "plan": plan,
            "summary": summary,
            "classifications": classifications,
            "validation": {
                "is_safe": validation_result.is_safe,
                "warnings": validation_result.warnings
            }
        }
    
    async def execute_plan(
        self,
        task_id: str,
        plan: PlanSchema,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Execute an approved plan.
        
        Args:
            task_id: Task identifier
            plan: Plan to execute
            dry_run: If True, only simulate execution
            
        Returns:
            Execution result dictionary
        """
        logger.info(f"Executing plan for task {task_id} (dry_run={dry_run})")
        
        result = await self.executor.execute_plan(plan, dry_run=dry_run)
        
        logger.info(f"Execution complete: {result.successful_actions} succeeded, "
                   f"{result.failed_actions} failed")
        
        return {
            "task_id": task_id,
            "success_count": result.successful_actions,
            "failure_count": result.failed_actions,
            "errors": result.error_message,
            "dry_run": dry_run
        }
    
    def _get_default_target_dirs(self) -> List[str]:
        """
        Get the default target directories for cleanup.
        
        Returns:
            List of directory paths
        """
        home = Path.home()
        
        default_dirs = [
            home / "Downloads",
            home / "Desktop",
            home / "Documents",
            home / "Videos"
        ]
        
        # Only return directories that exist
        return [str(d) for d in default_dirs if d.exists()]
    
    def _generate_summary(
        self,
        classifications: List[FileClassification],
        plan: PlanSchema
    ) -> Dict[str, Any]:
        """
        Generate summary statistics.
        
        Args:
            classifications: File classifications
            plan: Generated plan
            
        Returns:
            Summary dictionary
        """
        return {
            "total_files": len(classifications),
            "operations": len(plan.actions),
            "installers_found": sum(1 for c in classifications if c.is_installer),
            "archives_found": sum(1 for c in classifications if c.is_archive),
            "large_videos": sum(1 for c in classifications if c.is_large_video),
            "screenshots": sum(1 for c in classifications if c.is_screenshot),
            "duplicates": sum(1 for c in classifications if c.is_duplicate),
            "total_size_mb": sum(c.file.size_bytes for c in classifications) // (1024 * 1024)
        }
    
    def _create_fallback_plan(
        self,
        task_id: str,
        rule_matches: List,
        classifications: List[FileClassification]
    ) -> PlanSchema:
        """
        Create a simple fallback plan if AI planning fails.
        
        Uses the rule matches and classifications directly to create operations.
        
        Args:
            task_id: Task identifier
            rule_matches: Rule match results
            classifications: File classifications
            
        Returns:
            Simple plan based on classifications
        """
        from sentinel_core.models.planner import PlanAction
        from sentinel_core.models.enums import ActionType
        from pathlib import Path
        
        operations = []
        folders_to_create = set()
        home = Path.home()
        
        # Get scope path (parent of first file)
        scope_paths = {str(Path(c.file.path).parent) for c in classifications if c.file}
        scope_path = sorted(scope_paths)[0] if scope_paths else str(home / "Desktop")
        
        # Create operations from classifications
        for classification in classifications:
            if not classification.suggested_action:
                continue
                
            # Determine action type
            if classification.suggested_action == "delete":
                op_type = ActionType.DELETE
                dest_path = None
            elif classification.suggested_action == "move":
                op_type = ActionType.MOVE
                
                # Expand tilde path and create absolute path
                if classification.suggested_target and classification.suggested_target != "trash":
                    target = classification.suggested_target
                    # Expand ~
                    if target.startswith("~/"):
                        target = str(home / target[2:])
                    elif target == "~":
                        target = str(home)
                    
                    # Create destination path with filename
                    dest_dir = Path(target)
                    dest_path = str(dest_dir / Path(classification.file.path).name)
                    
                    # Track folders to create
                    folders_to_create.add(str(dest_dir))
                else:
                    # No valid target, skip this operation
                    continue
            else:
                # Unknown action, skip
                continue
            
            # Create the operation
            operation = PlanAction(
                type=op_type,
                source_path=classification.file.path,
                destination_path=dest_path,
                reason=f"{self._get_classification_reason(classification)}",
                confidence=0.75  # Fallback plans have lower confidence
            )
            operations.append(operation)
        
        return PlanSchema(
            task_id=task_id,
            scope_path=scope_path,
            folders_to_create=sorted(folders_to_create),
            actions=operations,
            summary=f"Organized {len(operations)} files using rule-based classification"
        )
    
    def _get_classification_reason(self, classification: FileClassification) -> str:
        """Get reason string for a classification."""
        if classification.is_installer:
            return f"Old installer ({classification.age_days} days)"
        if classification.is_archive:
            return "Archive file"
        if classification.is_large_video:
            return f"Large video ({classification.video_size_mb}MB)"
        if classification.is_screenshot:
            return "Screenshot"
        if classification.is_duplicate:
            return "Duplicate file"
        return "Organization"
