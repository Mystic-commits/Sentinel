import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from jinja2 import Template

from sentinel_core.models.filesystem import ScanResult
from sentinel_core.models.planner import PlanSchema
from sentinel_core.models.preferences import PreferencesSchema
from sentinel_core.rules.models import RuleMatchResult
from sentinel_core.planner.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class PlannerAgent:
    def __init__(self, ollama_client: OllamaClient, model_name: str = "llama2"):
        self.client = ollama_client
        self.model_name = model_name
        self._prompt_template = self._load_template()

    def _load_template(self) -> Template:
        """Loads the prompt template from disk."""
        # Assume template is in the same directory as this file
        template_path = Path(__file__).parent / "planner_prompt.txt"
        if not template_path.exists():
             raise FileNotFoundError(f"Prompt template not found at {template_path}")
        return Template(template_path.read_text(encoding="utf-8"))

    def create_plan(
        self, 
        task_id: str, 
        scan_result: ScanResult, 
        rule_matches: List[RuleMatchResult],
        preferences: PreferencesSchema
    ) -> PlanSchema:
        """
        Orchestrates the planning process:
        1. Formats context
        2. Generates prompt
        3. Calls LLM
        4. Validates output
        """
        
        # 1. Prepare Context (Simplify for LLM)
        files_summary = [
            {
                "path": f.path, 
                "name": f.name, 
                "type": f.file_type.value, 
                "size": f.size_bytes,
                "preview": f.preview_text[:100] if f.preview_text else None
            } 
            for f in scan_result.files
        ]
        
        matches_summary = [
            {
                "file": r.file_path,
                "rule": r.matched_rule,
                "category": r.suggested_category
            }
            for r in rule_matches if r.confidence > 0.8
        ]
        
        # 2. Render Prompt
        prompt = self._prompt_template.render(
            task_id=task_id,
            scope_path=scan_result.root_path,
            files_json=json.dumps(files_summary, indent=2),
            rule_matches_json=json.dumps(matches_summary, indent=2),
            preferences_json=preferences.model_dump_json(indent=2)
        )
        
        # 3. Generate
        logger.info(f"Generating plan for task {task_id} with model {self.model_name}")
        response_data = self.client.generate_json(prompt, model=self.model_name)
        
        # 4. Validate & Parse
        try:
            plan = PlanSchema(**response_data)
            return plan
        except Exception as e:
            logger.error(f"Failed to validate plan: {e}")
            logger.debug(f"Raw response: {response_data}")
            raise ValueError(f"LLM produced invalid plan schema: {e}")

