import re
import yaml
from pathlib import Path
from typing import List, Optional

from sentinel_core.models.filesystem import FileMetadata
from sentinel_core.rules.models import Rule, RuleMatchResult, RuleCondition

class RulesEngine:
    def __init__(self, rules_path: Optional[str] = None):
        self.rules: List[Rule] = []
        if rules_path and Path(rules_path).exists():
            self.load_rules(rules_path)
            
    def load_rules(self, rules_path: str):
        """Loads rules from a YAML file."""
        with open(rules_path, 'r') as f:
            data = yaml.safe_load(f)
            
        if not data or 'rules' not in data:
            print(f"DEBUG: No rules found in {rules_path}")
            return

        print(f"DEBUG: Loading {len(data['rules'])} rules from {rules_path}")

        for r_data in data['rules']:
            # - name: Invoice PDF
            #   category: Documents/Invoices
            #   priority: 10
            #   conditions:
            #     extension: .pdf
            #     name_contains: invoice
            
            conditions = []
            # Allow single condition block or list
            raw_conds = r_data.get('conditions', [])
            if isinstance(raw_conds, dict):
                raw_conds = [raw_conds]
                
            for rc in raw_conds:
                conditions.append(RuleCondition(**rc))
                
            rule = Rule(
                name=r_data['name'],
                category=r_data['category'],
                priority=r_data.get('priority', 100),
                conditions=conditions
            )
            self.rules.append(rule)
            
        # Sort by priority (ascending: 1 is higher than 100)
        self.rules.sort(key=lambda x: x.priority)

    def classify_files(self, files: List[FileMetadata]) -> List[RuleMatchResult]:
        """Classifies a list of files against loaded rules."""
        results = []
        for file in files:
            results.append(self._match_file(file))
        return results

    def _match_file(self, file: FileMetadata) -> RuleMatchResult:
        """Determines the best rule match for a single file."""
        
        for rule in self.rules:
            # A rule matches if ANY of its condition blocks match (OR logic between blocks)
            # Within a condition block, ALL fields must match (AND logic)
            
            for condition in rule.conditions:
                if self._check_condition(file, condition):
                    return RuleMatchResult(
                        file_path=file.path,
                        matched_rule=rule.name,
                        suggested_category=rule.category,
                        confidence=1.0, # Deterministic rules are high confidence
                        reason=f"Matched rule '{rule.name}'"
                    )
        
        # Fallback: Default categorization based on FileType
        return self._default_classification(file)

    def _check_condition(self, file: FileMetadata, condition: RuleCondition) -> bool:
        """Checks if a file satisfies a specific condition block."""
        
        if condition.extension and file.extension.lower() != condition.extension.lower():
            return False
            
        if condition.name_contains:
            if condition.name_contains.lower() not in file.name.lower():
                return False
                
        if condition.regex_pattern:
            if not re.search(condition.regex_pattern, file.name):
                return False
                
        if condition.min_size_bytes is not None:
            if file.size_bytes < condition.min_size_bytes:
                return False
                
        if condition.max_size_bytes is not None:
            if file.size_bytes > condition.max_size_bytes:
                return False
                
        return True

    def _default_classification(self, file: FileMetadata) -> RuleMatchResult:
        """Fallback heuristics."""
        category_map = {
            "document": "Documents",
            "image": "Images",
            "video": "Videos",
            "audio": "Audio",
            "archive": "Archives",
            "executable": "Installers",
            "code": "Code"
        }
        
        base_cat = category_map.get(file.file_type.value, "Misc")
        
        return RuleMatchResult(
            file_path=file.path,
            suggested_category=base_cat,
            confidence=0.5, # Low confidence for heuristic
            reason=f"Default type mapping for {file.file_type.value}"
        )
