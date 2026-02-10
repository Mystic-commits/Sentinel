from typing import List, Optional, Pattern
from pydantic import BaseModel, Field
import re

class RuleCondition(BaseModel):
    """A single condition for a rule match."""
    extension: Optional[str] = None # e.g. ".pdf"
    name_contains: Optional[str] = None # e.g. "invoice"
    regex_pattern: Optional[str] = None # e.g. "^[0-9]{4}-.*"
    min_size_bytes: Optional[int] = None
    max_size_bytes: Optional[int] = None

class Rule(BaseModel):
    """A classification rule."""
    name: str
    category: str # e.g. "Documents/Invoices"
    conditions: List[RuleCondition] # ANY condition match triggers rule? Or ALL? 
                                    # Logic: A rule usually has one set of criteria. 
                                    # Let's say IF extension=.pdf AND name_contains=invoice.
                                    # So these fields in RuleCondition should be ANDed.
                                    # If we need OR, we make multiple Rules.
    priority: int = 100 # Lower number = Higher priority

class RuleMatchResult(BaseModel):
    """Result of a classification attempt."""
    file_path: str
    matched_rule: Optional[str] = None
    suggested_category: Optional[str] = None
    confidence: float = 0.0
    reason: str = "No rule matched"
